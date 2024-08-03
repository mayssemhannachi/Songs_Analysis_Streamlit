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
    scope="user-read-recently-played user-top-read user-read-playback-state"
))

# Page config
st.set_page_config(page_title='Spotify Analysis', page_icon=':musical_note:', layout='wide', initial_sidebar_state='expanded')

# Load custom CSS with dynamic color
def load_css(color):
    css = f"""
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
    .st-emotion-cache-1wv6e1s {{
        color: {color};
    }}
    .st-emotion-cache-1wivap2 {{
        font-size: 14px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<div style="display: flex; align-items: center;">
    <img src="https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_CMYK_Green.png" width="100" style="margin-right: 20px;">
</div>
""", unsafe_allow_html=True)

# Display the user's profile details
user = sp.current_user()
st.sidebar.write(f"Logged in as {user.get('display_name', 'N/A')}")
if 'email' in user:
    st.sidebar.write(f"Email: {user.get('email', 'N/A')}")

# Display the app info
st.sidebar.subheader('About')
st.sidebar.info('''
This app allows you to analyze your Spotify listening habits.
- Enter the number of recently played tracks you want to analyze.
- View audio features, track popularity, top artists, and genre distribution.
- Powered by the Spotify API.
''')

# Display the title and description
st.sidebar.title('App Configuration 🎛️')



# Customization options
color = st.sidebar.color_picker('Pick a color', '#00f900')

# Apply the selected color to the CSS
load_css(color)



# Number of recently played tracks retrieved
number = st.sidebar.slider("Pick the number of recent played tracks you want to analyse", 0, 50)

st.sidebar.markdown('''
---
Created with ❤️ by [Mayssem Hn](https://github.com/mayssemhannachi/).''')


# Row A

# Fetch top tracks and artists
top_tracks = sp.current_user_top_tracks(limit=1)
top_artists = sp.current_user_top_artists(limit=1)

# Fetch currently playing track
currently_playing = sp.currently_playing()

# Display most played song, artist, and currently playing song 

st.markdown('### Basic Information')
col1, col2, col3 = st.columns(3)

# Display most played song
with col1:
    if top_tracks and top_tracks['items']:
        most_played_song = top_tracks['items'][0]['name']
        most_played_song_artist = top_tracks['items'][0]['artists'][0]['name']
        col1.metric('Most Played Song', f"{most_played_song} by {most_played_song_artist}")

# Display most played artist
with col2:
    if top_artists and top_artists['items']:
        most_played_artist = top_artists['items'][0]['name']
        col2.metric('Most Played Artist', most_played_artist)

# Display currently playing song
with col3:
    if currently_playing and currently_playing['is_playing']:
        currently_playing_song = currently_playing['item']['name']
        currently_playing_artist = currently_playing['item']['artists'][0]['name']
        col3.metric('Currently Playing', f"{currently_playing_song} by {currently_playing_artist}")
    else:
        col3.metric('Currently Playing', "No song is currently playing.")


with elements("new_element"):
    st.title('Spotify Songs Analysis')
    mui.Typography("Analyze your Spotify listening habits with Streamlit and the Spotify API!")




if number > 0:
    # Get the user's recently played tracks
    recently_played = sp.current_user_recently_played(limit=number+1)

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
