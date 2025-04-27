import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import pymysql
from sqlalchemy import create_engine

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

df=load_data()

st.title("🎬 Movie Insights Dashboard")

# 1. Top 10 Movies by Rating and Voting Counts
st.header("⭐ Top 10 Movies by Rating and Voting Counts")
top_movies = df.sort_values(by=["Rating", "Votes"], ascending=[False, False]).head(10)
fig = px.bar(top_movies, x="Title", y=["Rating", "Votes"], barmode='group', title="Top 10 Movies")
st.plotly_chart(fig)

# 2. Genre Distribution
st.header("🎞️ Genre Distribution")
genre_counts = df['Genre'].value_counts()
fig = px.bar(genre_counts, x=genre_counts.index, y=genre_counts.values, labels={'y':'Movie Count', 'x':'Genre'}, title="Movies per Genre")
st.plotly_chart(fig)

# 3. Average Duration by Genre
st.header("⏳ Average Duration by Genre")
avg_duration = df.groupby('Genre')['Duration'].mean().sort_values()
fig = px.bar(avg_duration, x=avg_duration.values, y=avg_duration.index, orientation='h', labels={'x':'Average Duration (min)', 'y':'Genre'}, title="Avg Duration by Genre")
st.plotly_chart(fig)

# 4. Voting Trends by Genre
st.header("🗳️ Voting Trends by Genre")
avg_votes = df.groupby('Genre')['Votes'].mean().sort_values(ascending=False)
fig = px.bar(avg_votes, x=avg_votes.index, y=avg_votes.values, labels={'y':'Average Votes', 'x':'Genre'}, title="Voting Trends")
st.plotly_chart(fig)

# 5. Rating Distribution
st.header("📊 Rating Distribution")
fig, ax = plt.subplots()
sns.histplot(df['Rating'], bins=20, kde=True, ax=ax)
ax.set_xlabel('Rating')
ax.set_ylabel('Count')
st.pyplot(fig)

# 6. Genre-Based Rating Leaders
st.header("🏆 Genre-Based Rating Leaders")
top_genre_movies = df.loc[df.groupby('Genre')['Rating'].idxmax()][['Genre', 'Title', 'Rating']]
st.dataframe(top_genre_movies)

# 7. Most Popular Genres by Voting
st.header("🥧 Most Popular Genres by Voting")
total_votes = df.groupby('Genre')['Votes'].sum()
fig = px.pie(values=total_votes.values, names=total_votes.index, title="Most Popular Genres (by Votes)")
st.plotly_chart(fig)

# 8. Duration Extremes
st.header("🔎 Duration Extremes")
shortest_movie = df.loc[df['Duration'].idxmin()]
longest_movie = df.loc[df['Duration'].idxmax()]
st.subheader("Shortest Movie 🎬")
st.metric(label="Movie", value=shortest_movie['Title'])
st.metric(label="Duration", value=f"{shortest_movie['Duration']} min")

st.subheader("Longest Movie 🎬")
st.metric(label="Movie", value=longest_movie['Title'])
st.metric(label="Duration", value=f"{longest_movie['Duration']} min")

# 9. Ratings by Genre (Heatmap)
st.header("🔥 Ratings by Genre Heatmap")
pivot_table = df.pivot_table(values='Rating', index='Genre', aggfunc='mean').sort_values('Rating', ascending=False)
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(pivot_table, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# 10. Correlation Analysis: Ratings vs Votes
st.header("📈 Correlation Analysis: Ratings vs Votes")
fig = px.scatter(df, x='Rating', y='V' \
'otes', trendline='ols', title="Ratings vs Votes")
st.plotly_chart(fig)
