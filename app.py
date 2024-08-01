import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Spotify credentials from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5500'

# Initialize Spotipy with OAuth authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='user-read-recently-played'
    )
)

# Set Streamlit page configuration
st.set_page_config(
    page_title='Spotify Song Analysis',
    page_icon='🎵',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Background image CSS
background_style = """
<style>
    body {
        background-image: url('https://example.com/your-image-url.jpg');
        background-size: cover;
    }
</style>
"""

# Display the background style
st.markdown(background_style, unsafe_allow_html=True)

# Streamlit UI
st.title('Analysis for Your Recently Played Spotify Songs')
st.write('Discover insights about your recent Spotify listening habits!')

#Number of recently played tracks retrieved
number = st.slider("Pick a number", 0, 100)

# Get the user's recently played tracks
recently_played = sp.current_user_recently_played(limit=number+2)

# Print the length of recently_played['items'] for debugging
print(f"Number of recently played tracks retrieved: {len(recently_played['items'])}")

# Check if there are tracks to process
if len(recently_played['items']) > 0:
    # Extract track details
    track_ids = []
    track_names = []
    artists = []
    release_dates = []
    popularity = []
    genres = []
    unique_tracks = set()
    
    for item in recently_played['items']:
        track_id = item['track']['id']
        track_name = item['track']['name']
        artist = item['track']['artists'][0]['name']
        release_date = item['track']['album']['release_date']
        track_popularity = item['track']['popularity']
        
        # Check for duplicates
        if track_id not in unique_tracks:
            track_ids.append(track_id)
            track_names.append(track_name)
            artists.append(artist)
            release_dates.append(release_date)
            popularity.append(track_popularity)
            unique_tracks.add(track_id)
            
            # Fetch genres for the artist
            artist_info = sp.artist(item['track']['artists'][0]['id'])
            genres.append(artist_info['genres'])

    # Fetch audio features for the unique recently played tracks
    audio_features = sp.audio_features(track_ids)

    # Create a DataFrame from audio features
    df = pd.DataFrame(audio_features)

    # Add track details to the DataFrame
    df['track_name'] = track_names
    df['artist'] = artists
    df['release_date'] = release_dates
    df['popularity'] = popularity
    df['genres'] = genres

    # Reorder columns for better readability
    df = df[['track_name', 'artist', 'release_date', 'popularity', 'genres', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
             'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']]

    # Set track_name as the index
    df.set_index('track_name', inplace=True)

    # Display audio features using a bar chart in Streamlit
    st.subheader('Audio Features of Your Recently Played Songs')
    st.bar_chart(df[['danceability', 'energy', 'loudness', 'valence', 'tempo']], height=500)

    # Track Popularity Analysis
    st.subheader('Track Popularity Analysis')
    st.bar_chart(df['popularity'], height=500)

    # Track Release Date Distribution
    st.subheader('Track Release Date Distribution')
    plt.figure(figsize=(10, 6))
    sns.histplot(pd.to_datetime(df['release_date']), kde=True, bins=20)
    st.pyplot(plt)

    # Top Artists
    st.subheader('Top Artists')
    top_artists = df['artist'].value_counts().head(10)
    st.bar_chart(top_artists)

    # Genre Distribution
    st.subheader('Genre Distribution')
    genre_list = [genre for sublist in df['genres'] for genre in sublist]
    genre_counts = pd.Series(genre_list).value_counts().head(10)
    st.bar_chart(genre_counts)

    # Optionally, display the DataFrame for more detailed analysis
    st.subheader('Raw Data')
    st.write(df)
else:
    st.write("No recently played tracks found. Make sure your Spotify account has sufficient data.")
