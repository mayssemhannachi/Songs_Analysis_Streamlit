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
        scope='user-top-read'
    )
)

# Set Streamlit page configuration
st.set_page_config(
    page_title='Spotify Song Analysis',
    page_icon='🎵',
    layout='centered',
    initial_sidebar_state='expanded'
)

# Streamlit UI
st.title('Analysis for your Top Spotify Songs')
st.write('Discover insights about your Spotify listening habits!')

# Get the user's top tracks
top_tracks = sp.current_user_top_tracks(limit=10, offset=0, time_range='long_term')

# Print the length of top_tracks['items'] for debugging
print(f"Number of top tracks retrieved: {len(top_tracks['items'])}")

# Check if there are tracks to process
if len(top_tracks['items']) > 0:
    # Extract track IDs for fetching audio features
    track_ids = [track['id'] for track in top_tracks['items']]

    # Fetch audio features for the top tracks
    audio_features = sp.audio_features(track_ids)

    # Create a DataFrame from audio features
    df = pd.DataFrame(audio_features)

    # Add track names to the DataFrame
    df['track_name'] = [top_tracks['items'][i]['name'] for i in range(min(10, len(top_tracks['items'])))]

    # Reorder columns for better readability
    df = df[['track_name', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
             'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']]

    # Set track_name as the index
    df.set_index('track_name', inplace=True)

    # Display audio features using a bar chart in Streamlit
    st.subheader('Audio Features of your Top Songs')
    st.bar_chart(df, height=500)

    # Optionally, display the DataFrame for more detailed analysis
    st.subheader('Raw Data')
    st.write(df)
else:
    st.write("No top tracks found. Make sure your Spotify account has sufficient data.")
