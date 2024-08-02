import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from streamlit_elements import elements, mui, html
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Check if environment variables are loaded correctly
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Print environment variables for debugging
print("Client ID:", client_id)
print("Client Secret:", client_secret)
print("Redirect URI:", redirect_uri)

# Initialize Spotify API client with credentials from .env file
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-read-recently-played"
))

# Streamlit UI
st.set_page_config(page_title='Spotify Analysis', page_icon=':musical_note:', layout='wide')
with elements("new_element"):
    st.title('Spotify Songs Analysis')
    mui.Typography("Analyze your Spotify listening habits with Streamlit and the Spotify API!")

# UI Color
color = st.color_picker("Pick A Color", "#FF4B4B")

# Inject custom CSS to style the sidebar and slider
st.markdown(f"""
    <style>
    .stSlider > div > div > div > div {{
        background: {color};
    }}
    .stSlider > div > div > div {{
        color: {color};
    }}
    .st-emotion-cache-10y5sf6 {{
        color: {color};
    }}
    .st-cl {{
        background: linear-gradient(to right, {color} 0%, {color} 60%, rgba(172, 177, 195, 0.25) 60%, rgba(172, 177, 195, 0.25) 100%);
    }}
    </style>
    """, unsafe_allow_html=True)

# Number of recently played tracks retrieved
number = st.slider("Pick a number", 0, 50)

if number > 0:
    # Get the user's recently played tracks
    recently_played = sp.current_user_recently_played(limit=number)

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
else:
    st.write("Please select a number greater than 0 to see the analysis.")
