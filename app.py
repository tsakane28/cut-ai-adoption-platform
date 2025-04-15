from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from dotenv import load_dotenv
from utils import preprocess_data, get_survey_stats
from model import train_model, predict_adoption
from openrouter_api import get_ai_insights
from data_viz import (
    create_ai_familiarity_chart, 
    create_tool_usage_chart,
    create_faculty_adoption_chart,
    create_challenges_chart,
    create_adoption_prediction_chart,
    create_suggestion_wordcloud
)
from database import (
    init_db,
    SessionLocal,
    load_survey_data_to_db,
    save_predictions_to_db,
    save_insight_to_db,
    get_surveys_from_db,
    surveys_to_dataframe
)
from loggers import get_logger

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
logger = get_logger("app")

# Initialize database
init_db()

# Global variables for data and model
app_data = None
app_model = None
app_predictions = None
app_insights = None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read and process data
        data = pd.read_csv(file)
        processed_data = preprocess_data(data)
        global app_data
        app_data = processed_data

        # Save to database
        added, skipped, skipped_emails = load_survey_data_to_db(processed_data)

        # Get basic statistics
        stats = get_survey_stats(processed_data)

        return jsonify({
            'success': True,
            'stats': stats,
            'added': added,
            'skipped': skipped,
            'skipped_emails': skipped_emails
        })
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    global app_data, app_model
    if app_data is None:
        return jsonify({'error': 'No data uploaded'}), 400

    try:
        model, accuracy = train_model(app_data)
        app_model = model
        return jsonify({'success': True, 'accuracy': accuracy})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualizations')
def get_visualizations():
    if app_data is None:
        return jsonify({'error': 'No data available'}), 400

    charts = {
        'familiarity': create_ai_familiarity_chart(app_data).to_json(),
        'tools': create_tool_usage_chart(app_data).to_json(),
        'faculty': create_faculty_adoption_chart(app_data).to_json(),
        'challenges': create_challenges_chart(app_data).to_json()
    }
    return jsonify(charts)

@app.route('/predict', methods=['POST'])
def predict():
    global app_data, app_model, app_predictions
    if app_data is None or app_model is None:
        return jsonify({'error': 'Data or model not ready'}), 400

    try:
        predictions = predict_adoption(app_model, app_data)
        app_predictions = predictions
        save_predictions_to_db(app_data, predictions)

        chart = create_adoption_prediction_chart(app_data, predictions).to_json()
        return jsonify({
            'success': True,
            'chart': chart,
            'average_prediction': predictions.mean()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/insights', methods=['POST'])
def generate_insights():
    global app_data, app_insights
    if app_data is None:
        return jsonify({'error': 'No data available'}), 400

    try:
        prompt = f"""
        Analyze this survey data about AI adoption at a university:
        - {len(app_data)} total responses
        - {app_data['3. Faculty'].nunique()} different faculties
        - {app_data['4. AI familiarity'].value_counts().to_dict()} AI familiarity levels
        - {app_data['5. Used AI tools'].value_counts().to_dict()} AI tools usage
        - Top challenges: {', '.join(app_data['8. Challenges'].value_counts().nlargest(3).index.tolist())}

        Provide 3-5 key insights about the AI adoption patterns observed, 
        and suggest 3 specific recommendations for increasing AI adoption at the university.
        Format your response as "Insights:" followed by numbered bullet points, then "Recommendations:" 
        followed by numbered bullet points.
        """
        insights = get_ai_insights(prompt)
        app_insights = insights
        save_insight_to_db(insights, 'general')
        return jsonify({'success': True, 'insights': insights})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/wordcloud')
def get_wordcloud():
    if app_data is None:
        return jsonify({'error': 'No data available'}), 400
    wordcloud_chart = create_suggestion_wordcloud(app_data["11. Suggestions"]).to_json()
    return jsonify({'wordcloud': wordcloud_chart})


@app.route('/admin/api_config')
def admin_api_config():
    api_key = get_api_key()
    model_id = get_model_id()
    model_name = get_model_name()
    if api_key:
        displayed_key = f"{api_key[:8]}...{api_key[-4:]}"
    else:
        displayed_key = "Not configured"
    return jsonify({
        'apiKey': displayed_key,
        'modelId': model_id,
        'modelName': model_name
    })

@app.route('/admin/db_config')
def admin_db_config():
    database_url = os.getenv("DATABASE_URL", "Not configured")
    if database_url and "@" in database_url:
        prefix = database_url.split("://")[0] if "://" in database_url else ""
        user_pwd = database_url.split("://")[1].split("@")[0] if "://" in database_url and "@" in database_url.split("://")[1] else ""
        host_db = database_url.split("@")[1] if "@" in database_url else ""
        if ":" in user_pwd:
            user = user_pwd.split(":")[0]
            masked_url = f"{prefix}://{user}:********@{host_db}"
        else:
            masked_url = database_url
    else:
        masked_url = database_url
    return jsonify({'databaseUrl': masked_url})


@app.route('/admin/env_vars')
def admin_env_vars():
    env_vars = {
        "PGHOST": os.getenv("PGHOST", "Not set"),
        "PGPORT": os.getenv("PGPORT", "Not set"),
        "PGDATABASE": os.getenv("PGDATABASE", "Not set"),
        "PGUSER": os.getenv("PGUSER", "Not set"),
        "OPENROUTER_MODEL_ID": os.getenv("OPENROUTER_MODEL_ID", "Not set"),
        "OPENROUTER_MODEL_NAME": os.getenv("OPENROUTER_MODEL_NAME", "Not set"),
    }
    return jsonify(env_vars)

@app.route('/admin/system_info')
def admin_system_info():
    import sys
    import platform
    system_info = {
        "Python Version": platform.python_version(),
        "Platform": platform.platform(),
        # "Streamlit Version": st.__version__,  # Removed Streamlit specific info
        "Pandas Version": pd.__version__,
        "NumPy Version": np.__version__,
    }
    return jsonify(system_info)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)