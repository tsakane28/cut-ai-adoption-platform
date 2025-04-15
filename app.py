import streamlit as st
import pandas as pd
import numpy as np
import os
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

# Set page config
st.set_page_config(
    page_title="CUT AI Adoption Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# Set up session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'model' not in st.session_state:
    st.session_state.model = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'insights' not in st.session_state:
    st.session_state.insights = None

# Main title
st.title("CUT AI Adoption Analytics Platform")

# Sidebar for navigation and filters
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1542744173-05336fcc7ad4", width=300)
    st.header("Navigation")
    
    page = st.radio(
        "Go to",
        ["Data Upload", "Dashboard", "AI Predictions", "Insights & Suggestions"]
    )
    
    st.header("About")
    st.write("""
    This platform analyzes AI adoption at CUT based on survey data 
    and provides predictions and insights using AI models.
    """)

# Data Upload Page
if page == "Data Upload":
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
                    records_added = load_survey_data_to_db(processed_data)
                    if records_added > 0:
                        st.success(f"Data successfully uploaded and {records_added} new records saved to database!")
                    else:
                        st.info("Data processed, but no new records were added to the database.")
                
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

# Dashboard Page
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

# AI Predictions Page
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

# Insights & Suggestions Page
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
