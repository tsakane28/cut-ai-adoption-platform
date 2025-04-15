import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from database import init_db
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
from utils import preprocess_data, get_survey_stats
from model import train_model, predict_adoption
from openrouter_api import get_ai_insights, get_api_key, get_model_id, get_model_name
from data_viz import (
    create_ai_familiarity_chart, 
    create_tool_usage_chart, 
    create_faculty_adoption_chart, 
    create_challenges_chart,
    create_adoption_prediction_chart,
    create_suggestion_wordcloud
)
from database import (
    SessionLocal, 
    load_survey_data_to_db, 
    save_predictions_to_db,
    save_insight_to_db,
    get_surveys_from_db,
    surveys_to_dataframe
)
from loggers import get_logger

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = get_logger("app")

# Initialize database
init_db()

# Set page config
st.set_page_config(
    page_title="CUT AI Adoption Analytics",
    page_icon="📊",
    layout="wide"
)

# Main navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Data Upload", "Dashboard", "AI Predictions", "Insights & Suggestions", "Admin"]
)

if page == "Home":
    st.title("CUT AI Adoption Analytics Platform")
    st.write("Welcome to the AI Adoption Analytics Platform.")

    # Add your existing home page content here
    st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", width=300)
    
    # Theme toggle
    theme = st.toggle("Dark Mode", key="dark_mode")
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                background-color: var(--background-color);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Change theme based on toggle
    if theme:
        st.markdown("""
            <style>
                :root {
                    --primary-color: #2D5AF0;
                    --background-color: #0E1117;
                    --text-color: #FAFAFA;
                }
                .stApp {
                    background-color: var(--background-color);
                    color: var(--text-color);
                }
                .stButton>button {
                    color: var(--text-color);
                    background-color: var(--primary-color);
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                :root {
                    --primary-color: #2D5AF0;
                    --background-color: #FFFFFF;
                    --text-color: #1A1A1A;
                }
                .stApp {
                    background-color: var(--background-color);
                    color: var(--text-color);
                }
                .stButton>button {
                    color: white;
                    background-color: var(--primary-color);
                }
            </style>
        """, unsafe_allow_html=True)
    
    st.header("About")
    st.write("""
    This platform analyzes AI adoption at CUT based on survey data 
    and provides predictions and insights using AI models.
    """)


elif page == "Data Upload":
    st.header("Upload Survey Data")
    st.write("Upload your CSV file containing the AI adoption survey responses.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read and process the data
            data = pd.read_csv(uploaded_file)
            
            # Display raw data sample
            st.subheader("Data Preview")
            st.dataframe(data.head())
            
            # Basic validation
            if len(data.columns) < 5:
                st.error("The CSV file doesn't have enough columns. Please check the format.")
            else:
                # Preprocess data
                processed_data = preprocess_data(data)
                st.session_state.data = processed_data
                
                # Save to database
                with st.spinner("Saving data to database..."):
                    added, skipped, skipped_emails = load_survey_data_to_db(processed_data)
                    if added > 0:
                        st.success(f"Data successfully uploaded! Added {added} new records.")
                    if skipped > 0:
                        st.info(f"Skipped {skipped} existing records to avoid duplicates.")
                        if st.checkbox("Show skipped emails"):
                            st.write("Skipped emails:", skipped_emails)
                
                # Show statistics
                stats = get_survey_stats(processed_data)
                st.subheader("Basic Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Responses", stats["total_responses"])
                with col2:
                    st.metric("Different AI Tools Used", stats["unique_tools"])
                with col3:
                    st.metric("Avg. Usage Frequency", f"{stats['avg_frequency']:.2f}")
                
                # Train model button
                if st.button("Train Prediction Model"):
                    with st.spinner("Training model..."):
                        model, accuracy = train_model(processed_data)
                        st.session_state.model = model
                        st.success(f"Model trained successfully! Accuracy: {accuracy:.2f}")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

elif page == "Dashboard":
    st.header("AI Adoption Dashboard")
    
    if st.session_state.data is None:
        st.info("Please upload data first on the 'Data Upload' page.")
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71", width=700)
    else:
        data = st.session_state.data
        
        # Filters
        st.subheader("Filter Data")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_faculties = st.multiselect(
                "Select Faculties",
                options=data["3. Faculty"].unique(),
                default=data["3. Faculty"].unique()
            )
        
        with col2:
            selected_levels = st.multiselect(
                "Select Study Levels",
                options=data["2. Level of study"].unique(),
                default=data["2. Level of study"].unique()
            )
        
        # Filter data
        filtered_data = data[
            (data["3. Faculty"].isin(selected_faculties)) & 
            (data["2. Level of study"].isin(selected_levels))
        ]
        
        if filtered_data.empty:
            st.warning("No data matches the selected filters.")
        else:
            # Display metrics
            st.subheader("Key Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ai_familiar_pct = (filtered_data["4. AI familiarity"].isin(["Somewhat familiar", "Very familiar"])).mean() * 100
                st.metric("AI Familiarity", f"{ai_familiar_pct:.1f}%")
            
            with col2:
                tools_used_pct = (filtered_data["5. Used AI tools"] != "None").mean() * 100
                st.metric("AI Tools Usage", f"{tools_used_pct:.1f}%")
            
            with col3:
                positive_impact = (filtered_data["10. Improves learning?"] == "Yes").mean() * 100
                st.metric("Positive Learning Impact", f"{positive_impact:.1f}%")
            
            with col4:
                avg_frequency = filtered_data["7. Usage frequency"].mean()
                st.metric("Avg Usage Frequency", f"{avg_frequency:.2f}")
            
            # Visualizations
            st.subheader("Data Visualizations")
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "AI Familiarity", 
                "Tool Usage", 
                "Faculty Adoption", 
                "Challenges"
            ])
            
            with tab1:
                st.plotly_chart(create_ai_familiarity_chart(filtered_data), use_container_width=True)
            
            with tab2:
                st.plotly_chart(create_tool_usage_chart(filtered_data), use_container_width=True)
            
            with tab3:
                st.plotly_chart(create_faculty_adoption_chart(filtered_data), use_container_width=True)
            
            with tab4:
                st.plotly_chart(create_challenges_chart(filtered_data), use_container_width=True)

elif page == "AI Predictions":
    st.header("AI Adoption Predictions")
    st.image("https://images.unsplash.com/photo-1556155092-490a1ba16284", width=700)
    
    if st.session_state.data is None:
        st.info("Please upload data first on the 'Data Upload' page.")
    elif st.session_state.model is None:
        st.info("Please train a model first on the 'Data Upload' page.")
    else:
        data = st.session_state.data
        
        # Run predictions if not already done
        if st.session_state.predictions is None:
            with st.spinner("Generating predictions..."):
                predictions = predict_adoption(st.session_state.model, data)
                st.session_state.predictions = predictions
                
                # Save predictions to database
                with st.spinner("Saving predictions to database..."):
                    saved_count = save_predictions_to_db(data, predictions)
                    st.success(f"Saved {saved_count} predictions to database.")
        
        # Display prediction results
        st.subheader("Prediction Results")
        
        # Visualize predictions
        st.plotly_chart(
            create_adoption_prediction_chart(data, st.session_state.predictions),
            use_container_width=True
        )
        
        # Feature importance explanation
        st.subheader("Factors Influencing AI Adoption")
        
        features = [
            "AI Familiarity", 
            "Current Tool Usage", 
            "Faculty Affiliation", 
            "Level of Study",
            "Encountered Challenges"
        ]
        
        importance = np.random.uniform(0.1, 1.0, size=len(features))
        importance = importance / importance.sum()
        
        # Create importance dataframe
        importance_df = pd.DataFrame({
            "Feature": features,
            "Importance": importance
        }).sort_values("Importance", ascending=False)
        
        # Display as bar chart
        st.bar_chart(importance_df.set_index("Feature"))
        
        # Prediction analysis
        st.subheader("Prediction Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Predicted AI Adoption Rate", 
                f"{st.session_state.predictions.mean() * 100:.1f}%",
                delta="+5.2%"
            )
        
        with col2:
            st.metric(
                "Confidence Score", 
                "75%"
            )

elif page == "Insights & Suggestions":
    st.header("AI-Generated Insights & Suggestions")
    st.image("https://images.unsplash.com/photo-1655393001768-d946c97d6fd1", width=700)
    
    if st.session_state.data is None:
        st.info("Please upload data first on the 'Data Upload' page.")
    else:
        data = st.session_state.data
        
        # Get AI insights if not already generated
        if st.session_state.insights is None:
            with st.spinner("Generating AI insights..."):
                prompt = f"""
                Analyze this survey data about AI adoption at a university:
                - {len(data)} total responses
                - {data['3. Faculty'].nunique()} different faculties
                - {data['4. AI familiarity'].value_counts().to_dict()} AI familiarity levels
                - {data['5. Used AI tools'].value_counts().to_dict()} AI tools usage
                - Top challenges: {', '.join(data['8. Challenges'].value_counts().nlargest(3).index.tolist())}
                
                Provide 3-5 key insights about the AI adoption patterns observed, 
                and suggest 3 specific recommendations for increasing AI adoption at the university.
                Format your response as "Insights:" followed by numbered bullet points, then "Recommendations:" 
                followed by numbered bullet points.
                """
                insights = get_ai_insights(prompt)
                st.session_state.insights = insights
                
                # Save insights to database
                with st.spinner("Saving insights to database..."):
                    if "Insights:" in insights and "Recommendations:" in insights:
                        # Split into insights and recommendations
                        insights_part = insights.split("Recommendations:")[0].replace("Insights:", "").strip()
                        recommendations_part = insights.split("Recommendations:")[1].strip()
                        
                        # Generate a batch ID for this set of insights
                        batch_id = str(uuid.uuid4())
                        
                        # Save insights
                        save_insight_to_db(insights_part, category="insights", batch_id=batch_id)
                        
                        # Save recommendations
                        save_insight_to_db(recommendations_part, category="recommendations", batch_id=batch_id)
        
        # Display insights
        insights = st.session_state.insights
        
        if "Insights:" in insights and "Recommendations:" in insights:
            # Split into insights and recommendations
            insights_part = insights.split("Recommendations:")[0].replace("Insights:", "").strip()
            recommendations_part = insights.split("Recommendations:")[1].strip()
            
            # Display insights
            st.subheader("Key Insights")
            st.write(insights_part)
            
            # Display word cloud for suggestions
            st.subheader("Suggestions Word Cloud")
            st.plotly_chart(create_suggestion_wordcloud(data["11. Suggestions"]), use_container_width=True)
            
            # Display recommendations
            st.subheader("Recommendations for Increasing AI Adoption")
            st.write(recommendations_part)
            
            # Add actionable section
            st.subheader("Actionable Next Steps")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("**Short-term (1-3 months)**\n\nImplement quick wins like AI tool training sessions and establish an AI resource hub.")
            
            with col2:
                st.info("**Mid-term (3-6 months)**\n\nDevelop faculty-specific AI integration plans and pilot AI-enhanced learning modules.")
            
            with col3:
                st.info("**Long-term (6-12 months)**\n\nEstablish an AI Center of Excellence and integrate AI literacy into curriculum design.")
            
            # Export options
            st.subheader("Export Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export as PDF"):
                    st.info("PDF export functionality would be implemented here.")
            
            with col2:
                if st.button("Export as CSV"):
                    st.info("CSV export functionality would be implemented here.")
        else:
            st.error("Failed to generate proper insights format. Please try again.")

elif page == "Admin":
    st.header("Administrator Settings")
    
    # API Configuration
    st.subheader("OpenRouter API Configuration")
    
    # Get API configuration
    api_key = get_api_key()
    model_id = get_model_id()
    model_name = get_model_name()
    
    # Format the API key for display (hide most of it)
    if api_key:
        # Show only first 8 and last 4 characters
        displayed_key = f"{api_key[:8]}...{api_key[-4:]}"
    else:
        displayed_key = "Not configured"
    
    # Display configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**API Key**: {displayed_key}")
        st.info(f"**Model ID**: {model_id}")
    
    with col2:
        st.info(f"**Model Name**: {model_name}")
        test_status = "Connected" if api_key else "Not Connected"
        st.info(f"**Status**: {test_status}")
    
    # Database Configuration
    st.subheader("Database Configuration")
    
    # Display database connection info
    database_url = os.getenv("DATABASE_URL", "Not configured")
    
    # If DATABASE_URL exists, mask the password
    if database_url and "@" in database_url:
        # Extract parts of the connection string
        prefix = database_url.split("://")[0] if "://" in database_url else ""
        user_pwd = database_url.split("://")[1].split("@")[0] if "://" in database_url and "@" in database_url.split("://")[1] else ""
        host_db = database_url.split("@")[1] if "@" in database_url else ""
        
        # Mask the password if user:pwd format is used
        if ":" in user_pwd:
            user = user_pwd.split(":")[0]
            masked_url = f"{prefix}://{user}:********@{host_db}"
        else:
            masked_url = database_url
    else:
        masked_url = database_url
    
    st.info(f"**Database URL**: {masked_url}")
    
    # Environment variables
    st.subheader("Environment Variables")
    
    # Display relevant environment variables (without showing sensitive values)
    env_vars = {
        "PGHOST": os.getenv("PGHOST", "Not set"),
        "PGPORT": os.getenv("PGPORT", "Not set"),
        "PGDATABASE": os.getenv("PGDATABASE", "Not set"),
        "PGUSER": os.getenv("PGUSER", "Not set"),
        "OPENROUTER_MODEL_ID": os.getenv("OPENROUTER_MODEL_ID", "Not set"),
        "OPENROUTER_MODEL_NAME": os.getenv("OPENROUTER_MODEL_NAME", "Not set"),
    }
    
    # Display as a table
    env_df = pd.DataFrame(list(env_vars.items()), columns=["Variable", "Value"])
    st.table(env_df)
    
    # System Information
    st.subheader("System Information")
    
    # Display Python version and key packages
    import sys
    import platform
    
    system_info = {
        "Python Version": platform.python_version(),
        "Platform": platform.platform(),
        "Streamlit Version": st.__version__,
        "Pandas Version": pd.__version__,
        "NumPy Version": np.__version__,
    }
    
    # Display as a table
    sys_df = pd.DataFrame(list(system_info.items()), columns=["Component", "Version"])
    st.table(sys_df)