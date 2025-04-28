import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import pymysql
from sqlalchemy import create_engine

# Inject custom CSS for background and styling
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://www.example.com/background.jpg'); /* Replace with your background URL or image */
        background-size: cover;
        background-position: center center;
    }
    .stTitle {
        color: white;
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
    }
    .stHeader {
        color: #FFD700; /* Gold color for header */
    }
    .stSubheader {
        color: #ADD8E6; /* Light blue for subheader */
    }
    .stText {
        color: #f0f0f0;
        font-family: 'Arial', sans-serif;
    }
    .stMetric {
        font-size: 1.2em;
        color: #ADD8E6; /* Color for metrics */
    }
    </style>
""", unsafe_allow_html=True)

# Connect to MySQL database
def get_connection():
    user = '43ar8iQYBuuTJzh.root'
    password = 'zhpR0aG2uWbHhVPh'
    host = 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'
    port = '4000'
    database = 'imdb'
    engine = create_engine("mysql+mysqlconnector://43ar8iQYBuuTJzh.root:zhpR0aG2uWbHhVPh@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/imdb")
    return engine

def load_data():
    try:
        engine = get_connection()
        query = "SELECT * FROM imdb_2024ml"  # Adjust to your actual table/fields
        df = pd.read_sql(query, engine)
        df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
        df['Duration_hours'] = df['Duration'] / 60
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if loading fails

df = load_data()

# Display Range for Duration, Rating, and Votes
if not df.empty:
    st.header("📊 Key Metrics Ranges")
    
    # Duration Range
    min_duration = df['Duration'].min()
    max_duration = df['Duration'].max()
    st.subheader("🎬 Duration Range")
    st.write(f"Minimum Duration: {min_duration} minutes")
    st.write(f"Maximum Duration: {max_duration} minutes")

    # Rating Range
    min_rating = df['Rating'].min()
    max_rating = df['Rating'].max()
    st.subheader("⭐ Rating Range")
    st.write(f"Minimum Rating: {min_rating}")
    st.write(f"Maximum Rating: {max_rating}")

    # Votes Range
    min_votes = df['Votes'].min()
    max_votes = df['Votes'].max()
    st.subheader("🗳️ Votes Range")
    st.write(f"Minimum Votes: {min_votes}")
    st.write(f"Maximum Votes: {max_votes}")

# Display Title and Header
st.title("🎬 Movie Insights Dashboard")

# Filter Options (Duration, Rating, Votes)
st.sidebar.header("Filters")
selected_genre = st.sidebar.selectbox("Select Genre", options=['All'] + list(df['Genre'].unique()))
min_duration_filter, max_duration_filter = st.sidebar.slider("Select Duration Range", min_value=min_duration, max_value=max_duration, value=(min_duration, max_duration))
min_rating_filter, max_rating_filter = st.sidebar.slider("Select Rating Range", min_value=min_rating, max_value=max_rating, value=(min_rating, max_rating))
min_votes_filter, max_votes_filter = st.sidebar.slider("Select Votes Range", min_value=min_votes, max_value=max_votes, value=(min_votes, max_votes))

# Filter Data Based on User Input
filtered_df = df[
    (df['Duration'] >= min_duration_filter) & (df['Duration'] <= max_duration_filter) &
    (df['Rating'] >= min_rating_filter) & (df['Rating'] <= max_rating_filter) &
    (df['Votes'] >= min_votes_filter) & (df['Votes'] <= max_votes_filter)
]

if selected_genre != 'All':
    filtered_df = filtered_df[filtered_df['Genre'] == selected_genre]

# Show filtered data summary
st.write(f"Showing {len(filtered_df)} movies after applying filters")

# 1. Top 10 Movies by Rating and Voting Counts
st.header("⭐ Top 10 Movies by Rating and Voting Counts")
top_movies = filtered_df.sort_values(by=["Rating", "Votes"], ascending=[False, False]).head(10)
fig = px.bar(top_movies, x="Title", y=["Rating", "Votes"], barmode='group', title="Top 10 Movies")
st.plotly_chart(fig)

# 2. Genre Distribution
st.header("🎞️ Genre Distribution")
genre_counts = filtered_df['Genre'].value_counts()
fig = px.bar(genre_counts, x=genre_counts.index, y=genre_counts.values, labels={'y':'Movie Count', 'x':'Genre'}, title="Movies per Genre")
st.plotly_chart(fig)

# 3. Average Duration by Genre
st.header("⏳ Average Duration by Genre")
avg_duration = filtered_df.groupby('Genre')['Duration'].mean().sort_values()
fig = px.bar(avg_duration, x=avg_duration.values, y=avg_duration.index, orientation='h', labels={'x':'Average Duration (min)', 'y':'Genre'}, title="Avg Duration by Genre")
st.plotly_chart(fig)

# 4. Voting Trends by Genre
st.header("🗳️ Voting Trends by Genre")
avg_votes = filtered_df.groupby('Genre')['Votes'].mean().sort_values(ascending=False)
fig = px.bar(avg_votes, x=avg_votes.index, y=avg_votes.values, labels={'y':'Average Votes', 'x':'Genre'}, title="Voting Trends")
st.plotly_chart(fig)

# 5. Rating Distribution
st.header("📊 Rating Distribution")
fig, ax = plt.subplots()
sns.histplot(filtered_df['Rating'], bins=20, kde=True, ax=ax)
ax.set_xlabel('Rating')
ax.set_ylabel('Count')
st.pyplot(fig)

# 6. Genre-Based Rating Leaders
st.header("🏆 Genre-Based Rating Leaders")
top_genre_movies = filtered_df.loc[filtered_df.groupby('Genre')['Rating'].idxmax()][['Genre', 'Title', 'Rating']]
st.dataframe(top_genre_movies)

# 7. Most Popular Genres by Voting
st.header("🥧 Most Popular Genres by Voting")
total_votes = filtered_df.groupby('Genre')['Votes'].sum()
fig = px.pie(values=total_votes.values, names=total_votes.index, title="Most Popular Genres (by Votes)")
st.plotly_chart(fig)

# 8. Duration Extremes
st.header("🔎 Duration Extremes")
shortest_movie = filtered_df.loc[filtered_df['Duration'].idxmin()]
longest_movie = filtered_df.loc[filtered_df['Duration'].idxmax()]
st.subheader("Shortest Movie 🎬")
st.metric(label="Movie", value=shortest_movie['Title'])
st.metric(label="Duration", value=f"{shortest_movie['Duration']} min")

st.subheader("Longest Movie 🎬")
st.metric(label="Movie", value=longest_movie['Title'])
st.metric(label="Duration", value=f"{longest_movie['Duration']} min")

# 9. Ratings by Genre (Heatmap)
st.header("🔥 Ratings by Genre Heatmap")
pivot_table = filtered_df.pivot_table(values='Rating', index='Genre', aggfunc='mean').sort_values('Rating', ascending=False)
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(pivot_table, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# 10. Correlation Analysis: Ratings vs Votes
st.header("📈 Correlation Analysis: Ratings vs Votes")
fig = px.scatter(filtered_df, x='Rating', y='Votes', trendline='ols', title="Ratings vs Votes")
st.plotly_chart(fig)
