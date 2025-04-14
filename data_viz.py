import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

def create_ai_familiarity_chart(data):
    """
    Create a chart showing AI familiarity distribution
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Get familiarity counts
    familiarity_counts = data["4. AI familiarity"].value_counts().reset_index()
    familiarity_counts.columns = ["Familiarity Level", "Count"]
    
    # Create a categorical order
    familiarity_order = ["Not familiar at all", "Somewhat familiar", "Very familiar"]
    
    # Create the chart
    fig = px.bar(
        familiarity_counts,
        x="Familiarity Level",
        y="Count",
        color="Familiarity Level",
        color_discrete_map={
            "Not familiar at all": "#FFC857",
            "Somewhat familiar": "#17C3B2",
            "Very familiar": "#2D5AF0"
        },
        category_orders={"Familiarity Level": familiarity_order},
        title="AI Familiarity Distribution"
    )
    
    fig.update_layout(
        xaxis_title="Familiarity Level",
        yaxis_title="Number of Respondents",
        legend_title="Familiarity Level"
    )
    
    return fig

def create_tool_usage_chart(data):
    """
    Create a chart showing AI tool usage
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Extract all tools mentioned in the survey
    all_tools = []
    for tools in data["6. Tools used"].dropna():
        if tools != "None":
            all_tools.extend([tool.strip() for tool in tools.split(",")])
    
    # Count tool occurrences
    tool_counts = Counter(all_tools)
    
    # Convert to dataframe
    tool_df = pd.DataFrame.from_dict(tool_counts, orient="index", columns=["Count"]).reset_index()
    tool_df.columns = ["Tool", "Count"]
    
    # Sort by count
    tool_df = tool_df.sort_values("Count", ascending=False).head(10)
    
    # Create chart
    fig = px.bar(
        tool_df,
        x="Count",
        y="Tool",
        color="Count",
        color_continuous_scale=["#17C3B2", "#2D5AF0"],
        orientation="h",
        title="Top 10 AI Tools Used"
    )
    
    fig.update_layout(
        xaxis_title="Number of Users",
        yaxis_title="AI Tool",
        yaxis={"categoryorder": "total ascending"}
    )
    
    return fig

def create_faculty_adoption_chart(data):
    """
    Create a chart showing AI adoption by faculty
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Group by faculty and calculate adoption metrics
    faculty_data = data.groupby("3. Faculty").agg({
        "adoption_positive": "mean",
        "tools_count": "mean",
        "1. Email": "count"
    }).reset_index()
    
    faculty_data.columns = ["Faculty", "Positive Impact Rate", "Avg Tools Used", "Response Count"]
    
    # Calculate sizes for bubble chart
    faculty_data["Size"] = faculty_data["Response Count"] / faculty_data["Response Count"].max() * 50
    
    # Create chart
    fig = px.scatter(
        faculty_data,
        x="Avg Tools Used",
        y="Positive Impact Rate",
        size="Size",
        color="Faculty",
        hover_name="Faculty",
        text="Faculty",
        size_max=40,
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="AI Adoption by Faculty"
    )
    
    fig.update_layout(
        xaxis_title="Average Number of AI Tools Used",
        yaxis_title="Percentage Reporting Positive Impact",
        yaxis={"tickformat": ".0%"}
    )
    
    fig.update_traces(textposition="top center")
    
    return fig

def create_challenges_chart(data):
    """
    Create a chart showing challenges faced in AI adoption
    
    Args:
        data (pd.DataFrame): Processed survey data
        
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Extract all challenges mentioned in the survey
    all_challenges = []
    for challenges in data["8. Challenges"].dropna():
        if challenges != "None":
            all_challenges.extend([challenge.strip() for challenge in challenges.split(",")])
    
    # Count challenge occurrences
    challenge_counts = Counter(all_challenges)
    
    # Convert to dataframe
    challenge_df = pd.DataFrame.from_dict(challenge_counts, orient="index", columns=["Count"]).reset_index()
    challenge_df.columns = ["Challenge", "Count"]
    
    # Sort by count and get top challenges
    challenge_df = challenge_df.sort_values("Count", ascending=False).head(8)
    
    # Create chart
    fig = px.pie(
        challenge_df,
        values="Count",
        names="Challenge",
        color_discrete_sequence=px.colors.sequential.Teal,
        title="Challenges in AI Adoption"
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_adoption_prediction_chart(data, predictions):
    """
    Create a chart visualizing adoption predictions
    
    Args:
        data (pd.DataFrame): Processed survey data
        predictions (array): Model predictions
        
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Create a dataframe with predictions
    pred_df = pd.DataFrame({
        "Faculty": data["3. Faculty"],
        "Level": data["2. Level of study"],
        "AI Familiarity": data["4. AI familiarity"],
        "Adoption Probability": predictions
    })
    
    # Group by faculty and level
    grouped_preds = pred_df.groupby(["Faculty", "Level"]).agg({
        "Adoption Probability": "mean"
    }).reset_index()
    
    # Create the chart
    fig = px.bar(
        grouped_preds,
        x="Faculty",
        y="Adoption Probability",
        color="Level",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Predicted AI Adoption by Faculty and Study Level"
    )
    
    fig.update_layout(
        xaxis_title="Faculty",
        yaxis_title="Predicted Adoption Probability",
        yaxis={"tickformat": ".0%"},
        legend_title="Study Level"
    )
    
    return fig

def create_suggestion_wordcloud(suggestions):
    """
    Create a word cloud visualization from suggestions
    
    Args:
        suggestions (Series): Series of suggestion texts
        
    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure
    """
    # Combine all suggestions
    all_text = " ".join([str(s) for s in suggestions if not pd.isna(s)])
    
    # Count word frequencies (simple approach)
    words = all_text.lower().split()
    word_counts = Counter(words)
    
    # Remove common words
    stopwords = ["the", "and", "to", "of", "in", "for", "on", "with", "a", "an", "that", "this", "is", "are"]
    for word in stopwords:
        if word in word_counts:
            del word_counts[word]
    
    # Create dataframe from word counts
    word_df = pd.DataFrame({
        "word": list(word_counts.keys()),
        "count": list(word_counts.values())
    })
    
    # Take top 30 words
    word_df = word_df.sort_values("count", ascending=False).head(30)
    
    # Calculate size for scatter plot
    word_df["size"] = word_df["count"] / word_df["count"].max() * 40
    
    # Create a scatter plot simulation of a word cloud
    fig = go.Figure()
    
    # Create a grid of positions
    n = len(word_df)
    positions = []
    cols = int(np.sqrt(n)) + 1
    for i in range(n):
        row = i // cols
        col = i % cols
        # Add some jitter
        x = col + np.random.uniform(-0.3, 0.3)
        y = row + np.random.uniform(-0.3, 0.3)
        positions.append((x, y))
    
    # Add words as scatter points
    for i, (word, count, size) in enumerate(zip(word_df["word"], word_df["count"], word_df["size"])):
        x, y = positions[i]
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode="text",
            text=[word],
            hoverinfo="text",
            hovertext=f"{word}: {count}",
            textfont=dict(
                size=size,
                color=px.colors.sequential.Turbo[i % len(px.colors.sequential.Turbo)]
            )
        ))
    
    fig.update_layout(
        title="Suggestion Word Cloud",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white"
    )
    
    return fig
