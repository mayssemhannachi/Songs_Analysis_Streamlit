from collections import defaultdict
import requests
import streamlit as st
import pandas as pd
from spotipy import SpotifyException
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import time
import base64
import requests_cache



# Load environment variables from .env file
load_dotenv()

# Check if environment variables are loaded correctly
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Verify that all environment variables are loaded
if not client_id or not client_secret or not redirect_uri:
    raise ValueError("One or more environment variables are missing. Please check your .env file.")

# Initialize requests cache
requests_cache.install_cache('spotify_cache', expire_after=3600)  # Cache expires after 1 hour

# Initialize Spotify API client with credentials from .env file
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-read-recently-played user-top-read user-read-playback-state",
        requests_timeout=30  # Increase the timeout to 30 seconds
    ))
    print('Spotify API client created successfully!')
except Exception as e:
    print(f"Error initializing Spotify API client: {e}")
    st.error(f"Error initializing Spotify API client: {e}")


print('Spotify API client created successfully!')

# Page config
st.set_page_config(page_title='HarmonyHub', page_icon='🎵', layout='wide', initial_sidebar_state='expanded')



# Load the CSS file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Display the user's profile details
# Fetch the user's profile details with caching
session = requests_cache.CachedSession()
access_token = sp.auth_manager.get_cached_token()['access_token']
response = session.get('https://api.spotify.com/v1/me', headers={"Authorization": f"Bearer {access_token}"})
user = response.json()



# Display the user's profile details
user = sp.current_user()
profile_image_url = None
if 'images' in user and user['images']:
    profile_images = user['images']
    profile_images.sort(key=lambda img: img['width'] * img['height'], reverse=True)
    profile_image_url = profile_images[0]['url']

# Display the profile picture
if profile_image_url:
    st.sidebar.image(profile_image_url, width=130)

# Display the user's display name
st.sidebar.title(f"{user['display_name']}")

# Number of followers
st.sidebar.write(f"{user['followers']['total']} followers")

# User's Spotify link and logo in the sidebar
spotify_logo_url = "https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg"
spotify_link = user['external_urls']['spotify']

st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center;">
        <img src="{spotify_logo_url}" width="30" style="margin-right: 10px;">
        <a href="{spotify_link}" target="_blank" style="color: #1DB954;">Open in Spotify</a>
    </div>
""", unsafe_allow_html=True)



# Three columns with different widths
col1, col2, col3 = st.columns([6, 5, 5])

# Add the header with the app name
with col1:
    st.title("HarmonyHub 🎧ྀི")

# Song playing


with col3:
    current_track = sp.current_playback()
    if current_track:
        background_color = "#1DB954"  # You can change this to any color you prefer

        # Load Lottie animation
        file_ = open("/Users/macbookair/Documents/Data Science Learning/5.ETL/2. Analyse  Songs With The Spotify API/player2.gif", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()

        # Display the song's details
        st.markdown(f"""
                <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; display: flex; align-items: center;">
                    <img src="{current_track['item']['album']['images'][0]['url']}" width="40" style="margin-right: 20px; border-radius:5px;">
                    <div style="flex-grow: 1;">
                        <div style="display: flex; align-items: center;">
                            <p style="margin: 0; font: sans-serif; font-weight: 700;">{current_track['item']['name']} </p>
                            <img src="data:image/gif;base64,{data_url}" alt="player" style="width: 30px; height: 25px; margin-left: 20px;">
                        </div>
                        <p style="margin: 0; color: black; font: sans-serif; font-weight: 700;">{current_track['item']['artists'][0]['name']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        

print('User profile details displayed successfully!')

# Add space between Row A and Row B
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

print("extracting data")
#data i will work on 
# Fetch top tracks with caching
session = requests_cache.CachedSession()
try:
    print("Fetching top tracks...")
    response = session.get('https://api.spotify.com/v1/me/top/tracks?limit=50', headers={
        "Authorization": f"Bearer {sp.auth_manager.get_access_token(as_dict=False)}"
    })
    response.raise_for_status()
    top_tracks = response.json()
    print("Top tracks fetched successfully.")
except Exception as e:
    print(f"Error fetching top tracks: {e}")
    st.error(f"Error fetching top tracks: {e}")

# Cache for genres
genres_cache = defaultdict(list)

# Function to fetch genres with retry logic
def fetch_genres_with_retry(artist_id, retries=3, delay=5):
    if artist_id in genres_cache:
        return genres_cache[artist_id]
    
    for attempt in range(retries):
        try:
            response = session.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers={
                "Authorization": f"Bearer {sp.auth_manager.get_access_token(as_dict=False)}"
            }, timeout=10)  # Set a timeout of 10 seconds
            response.raise_for_status()
            genres = response.json().get('genres', [])
            genres_cache[artist_id] = genres
            return genres
        except requests.exceptions.RequestException as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", delay))
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Request error fetching genres for artist (ID: {artist_id}): {e}")
                return []
        except Exception as e:
            print(f"Unexpected error fetching genres for artist (ID: {artist_id}): {e}")
            return []
    return []

# Initialize data list
data = []

# Process each track
try:
    for track in top_tracks['items']:
        track_id = track['id']
        album = track['album']
        album_name = album['name']
        album_image_url = album['images'][0]['url'] if album['images'] else None
        artist_name = album['artists'][0]['name']
        popularity = track['popularity']
        duration_ms = track['duration_ms']
        
        # Fetch genres of the artist
        try:
            print(f"Fetching genres for artist: {artist_name}")
            artist_id = album['artists'][0]['id']
            genres = fetch_genres_with_retry(artist_id)
            print(f"Genres for artist {artist_name}: {genres}")
        except Exception as e:
            print(f"Error fetching genres for artist {artist_name} (ID: {artist_id}): {e}")
            genres = []

        # Append track data to the list
        data.append({
            'track_id': track_id,
            'track_name': track['name'],
            'album_name': album_name,
            'album_image_url': album_image_url,
            'artist_name': artist_name,
            'genres': genres,
            'popularity': popularity,
            'duration_ms': duration_ms
        })
        print(f"Processed track: {track['name']} by {artist_name}")

# Create DataFrame
    df = pd.DataFrame(data)
    print("DataFrame created successfully.")
    print(df.head())
except Exception as e:
    print(f"Error processing tracks: {e}")
    st.error(f"Error processing tracks: {e}")



# Debugging: Print the 'genres' column to the console
print("Genres column:")
print(df['genres'])


col1, col2 = st.columns([5, 5])

# Fetch top artists with caching
session = requests_cache.CachedSession()
response = session.get('https://api.spotify.com/v1/me/top/artists?limit=20', headers={
    "Authorization": f"Bearer {sp.auth_manager.get_access_token(as_dict=False)}"
})
top_artists = response.json()


# Display the user's top artists
with col1:
    st.header("Top Artists")

    # Display the top 3 artists' pictures next to each other
    top_3_artists = top_artists['items'][:3]
    artist_images_html = ""
    for artist in top_3_artists:
        artist_image_url = artist['images'][0]['url'] if artist['images'] else None
        if artist_image_url:
            artist_images_html += f'<img src="{artist_image_url}" alt="{artist["name"]}">'

    st.markdown(
        f"""
        <div class="circles-gallery" >
            {artist_images_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    # Display the top 9 artists' names
    for i, artist in enumerate(top_artists['items'][:9]):
        # Extract the artist's name and image URL
        artist_name = artist['name']
        artist_image_url = artist['images'][0]['url'] if artist['images'] else None

        # Display the artist's details within a div with custom background color
        st.markdown(
            f"""
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                <p style="color: white; opacity: 0.5; margin-right: 20px; font-weight:200; font-size:20px;">{i+1}</p>
                {'<img src="' + artist_image_url + '" width="50" height="50" style="border-radius: 50%; margin-right: 10px;">' if artist_image_url else ''}
                <p style="color: white; line-height: 30px;">{artist_name}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


    # see more button
    st.markdown(
        f"""
        <div class="see-all-btn" >
            <a href="https://open.spotify.com/collection/artists" target="_blank">SEE ALL</a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.header("Top Tracks")
    # Get the user's top tracks with the picture
    top_tracks_images = []
    for track in top_tracks['items']:
        track_image = track['album']['images'][0]['url'] if track['album']['images'] else None
        top_tracks_images.append(track_image)

    # top 3 tracks
    top_3_tracks = top_tracks_images[:3]
    track_images_html = ""
    for track_image in top_3_tracks:
        if track_image:
            track_images_html += f'<img src="{track_image}" alt="Track Image">'

    st.markdown(
        f"""
        <div class="square-gallery " >
            {track_images_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display the top tracks
    for i, track in enumerate(top_tracks['items'][:9]):
        track_name = track['name']
        track_image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
        artist_name = track['artists'][0]['name']

        st.markdown(
            f"""
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
             <p style="color: white; opacity: 0.5; margin-right: 20px; font-weight:200; font-size:20px;">{i+1}</p>
            {'<img src="' + track_image_url + '" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">' if track_image_url else ''}
            <div style="flex-grow: ;">
            <p style="color: white; margin-bottom: 2px;">{track_name} </p>
            <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{artist_name}</p>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # see more button
    st.markdown(
        f"""
        <div class="see-all-btn" >
            <a href="https://open.spotify.com/collection/tracks" target="_blank">SEE ALL</a>
        </div>
        """,
        unsafe_allow_html=True
    )
# Add space between Row A and Row B
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)


col1, col2 = st.columns([5, 5])


# Extract user's most listened songs details


# Count the number of songs listened to for each album
album_counts = df['album_name'].value_counts().reset_index()
album_counts.columns = ['album_name', 'count']

# Merge the counts with the original DataFrame to get album details
top_albums_df = pd.merge(album_counts, df.drop_duplicates(subset=['album_name']), on='album_name')

with col1:
    # Display the top albums
    st.header("Top Albums")

    # Display the top 3 albums' pictures next to each other
    top_3_albums = top_albums_df.head(3)
    album_images_html = ""
    for _, album in top_3_albums.iterrows():
        album_image_url = album['album_image_url']
        if album_image_url:
            album_images_html += f'<img src="{album_image_url}" alt="{album["album_name"]}">'

    st.markdown(
        f"""
        <div class="square-gallery" >
            {album_images_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display the top albums
    for i, album in top_albums_df.head(9).iterrows():
        album_name = album['album_name']
        album_image_url = album['album_image_url']
        artist_name = album['artist_name']

        st.markdown(
            f"""
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                <p style="color: white; opacity: 0.5; margin-right: 20px; font-weight:200; font-size:20px;">{i+1}</p>
                {'<img src="' + album_image_url + '" width="50" height="50" style="border-radius: 10%; margin-right: 10px;">' if album_image_url else ''}
                <div>
                    <p style="color: white; line-height: 30px; margin: 0;">{album_name}</p>
                    <p style="color: white; opacity: 0.5; margin: 0;">{artist_name}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # see more button
    st.markdown(
        f"""
        <div class="see-all-btn" >
            <a href="https://open.spotify.com/collection/albums" target="_blank">SEE ALL</a>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    # Display the top albums
    st.header("Top Genres")

    # Ensure genres is a Series with value counts
    top_genres = df.explode('genres')['genres'].value_counts().head(9)


    # Display the top genres
    for i, (genre, count) in enumerate(top_genres.items()):
        st.markdown(
            f"""
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; gap:20px;height: 70px;"> 
                <p style="color: white; opacity: 0.5; margin-right: 20px; font-size:20px; margin: 0;">{i+1}</p>
                <p style="color: white; line-height: 30px; margin: 0; font-weight:800; text-transform: capitalize;">{genre}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # see more button
    st.markdown(
        f"""
        <div class="see-all-btn" >
            <a href="https://open.spotify.com/collection/genres" target="_blank">SEE ALL</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# Add space between Row A and Row B
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Display the user's taste in music

# Function to fetch and process track features
def fetch_track_features(sp, track_ids):
    batch_size = 50  # Number of tracks to process in each batch
    max_retries = 5  # Maximum number of retries
    
    track_features = []
    session = requests_cache.CachedSession()  # Use cached session

    # Loop through the track IDs in batches
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]

        print(f"Fetching batch {i // batch_size + 1}: {batch}")  # Debug statement to show current batch

        retry_delay = 1  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                response = session.get(f"https://api.spotify.com/v1/audio-features?ids={','.join(batch)}", headers={
                    "Authorization": f"Bearer {sp.auth_manager.get_access_token(as_dict=False)}"
                })

                response.raise_for_status()
                audio_features = response.json()['audio_features']

                if audio_features is None:
                    print(f"No audio features returned for batch {i // batch_size + 1}")
                    break

                for idx, features in enumerate(audio_features):
                    if features is not None:
                        mood = 'Sad' if features['valence'] <= 0.5 else 'Happy'
                        rhythm = 'Danceable' if features['danceability'] >= 0.5 else 'Unrhythmic'
                        tempo = 'Fast' if features['tempo'] >= 120 else 'Slow'
                        acoustic = 'Acoustic' if features['acousticness'] >= 0.5 else 'Electric'
                        energy = 'Energetic' if features['energy'] >= 0.5 else 'Relaxing'
                        loudness = 'Soft' if features['loudness'] >= -5 else 'Loud'
                        instrumental = 'Instrumental' if features['instrumentalness'] >= 0.5 else 'With Vocals'
                        live = 'Live' if features['liveness'] >= 0.5 else 'Studio'
                        spoken = 'Spoken' if features['speechiness'] >= 0.5 else 'Musical'

                        track_features.append({
                            'track_id': batch[idx],
                            'mood': mood,
                            'rhythm': rhythm,
                            'tempo': tempo,
                            'acoustic': acoustic,
                            'energy': energy,
                            'loudness': loudness,
                            'instrumental': instrumental,
                            'live': live,
                            'spoken': spoken
                        })

                break  # Exit the retry loop on success

            except SpotifyException as e:
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', 5))  # Retry after 'Retry-After' seconds or default to 5 seconds
                    print(f"Rate limit exceeded, retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                elif e.http_status in [502, 503]:
                    # Handle server errors with exponential backoff
                    print(f"Server error (HTTP {e.http_status}), retrying after {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Double the delay for the next retry
                else:
                    print(f"Error fetching audio features: {e}")
                    raise e  # Re-raise the exception if it's not a rate limit or server issue

            if attempt == max_retries - 1:
                print(f"Failed to fetch audio features for batch {i // batch_size + 1} after {max_retries} attempts")

    return track_features

# Example usage:
# Assuming `sp` is an authenticated Spotipy client and `df` contains user's top tracks with `track_id`
track_ids = [track['id'] for track in top_tracks['items']]  # Replace `top_tracks['items']` with your top tracks data

# Print track IDs to verify they are valid
print("Track IDs:", track_ids)

# Fetch and process audio features
track_features = fetch_track_features(sp, track_ids)

# Check if track_features is empty
if not track_features:
    print("No track features were fetched. Check your Spotify API usage or track IDs.")
else:
    # Convert the list of track features to a DataFrame
    df_features = pd.DataFrame(track_features)

    # Debugging: Print the DataFrame columns to check if all expected columns are present
    print("DataFrame columns:", df_features.columns)

    # Debugging: Print the first few rows of the DataFrame to check the data
    print(df_features.head())

    # Define all possible criteria and their opposites
    criteria_opposites = {
        'mood': ('Sad', 'Happy'),
        'rhythm': ('Unrhythmic', 'Danceable'),
        'tempo': ('Slow', 'Fast'),
        'acoustic': ('Acoustic', 'Electric'),
        'energy': ('Relaxing', 'Energetic'),
        'loudness': ('Soft', 'Loud'),
        'instrumental': ('Instrumental', 'With Vocals'),
        'live': ('Live', 'Studio'),
        'spoken': ('Spoken', 'Musical')
    }

    # Initialize the DataFrame with all possible criteria and their opposites
    columns = [opposite for pairs in criteria_opposites.values() for opposite in pairs]
    percentages_df = pd.DataFrame(0, index=criteria_opposites.keys(), columns=columns)

    # Calculate the percentage of each category
    for criterion in criteria_opposites.keys():
        if criterion in df_features.columns:
            value_counts = df_features[criterion].value_counts(normalize=True) * 100
            print(f"Value counts for '{criterion}':")
            print(value_counts)
            
            # Assign these values to the correct locations in percentages_df
            for category, percentage in value_counts.items():
                if category in percentages_df.columns:
                    percentages_df.at[criterion, category] = percentage

    # Ensure all criteria and their opposites are included in percentages_df with default 0% if missing
    for criterion, (negative, positive) in criteria_opposites.items():
        if criterion not in percentages_df.index:
            percentages_df.loc[criterion] = [0] * len(percentages_df.columns)
        if negative not in percentages_df.columns:
            percentages_df[negative] = 0
        if positive not in percentages_df.columns:
            percentages_df[positive] = 0

    # Debugging: Print the DataFrame to check the data
    print("Final DataFrame with percentages:")
    print(percentages_df)


# Display the user's music taste statistics
st.header("Taste")



# CSS content for the grid display
css_content = """
    <style>
    .outer-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr); /* 3 columns with equal width */
        gap: 10px; /* Space between outer grid items */
        padding: 50px;
        border-radius: 10px;
        background-color: #14171d;
        width: fit-content;
    }

    .grid-item {
        border-radius: 10px;
        padding: 30px;
        display: flex;
        align-items: center;
        justify-content: center; /* Center the content */
        color: white;
        font-weight: 800;
        font-size: 14px;
        height: 40px; /* Set a fixed height for uniform grid items */
        width: 385px;
        background-color: #14171d; /* Add background color */
    }

    span {
        margin: 10px;
    }

    .slider-container {
        width: fit-content;
    }

    .slider {
        -webkit-appearance: none;
        width: 100px;
        height: 10px;
        background: #6e6e6e;
        border-radius: 20px;
        outline: none;
        opacity: 0.8;
        transition: opacity .15s ease-in-out;
    }

    .slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 8px;
        height: 15px;
        background: #1DB954;
        border-radius: 22px;
        box-shadow: 0px 10px 10px rgba(0,0,0,0.25);
        border: 0px solid #ffffff;
    }

    .slider::-moz-range-thumb {
        width: 8px;
        height: 15px;
        background: #1DB954;
        border-radius: 22px;
        cursor: pointer;
        border: 0px solid #ffffff;
    }
    </style>
    """

# Inject the CSS into the Streamlit app
st.markdown(css_content, unsafe_allow_html=True)



# Create a grid layout using Streamlit's columns
columns = st.columns(3)

# Loop through the criteria and add items to the grid
for i, (criterion, (left_value, right_value)) in enumerate(criteria_opposites.items()):
    if criterion in percentages_df.index:
        values = percentages_df.loc[criterion].dropna().sort_values(ascending=False)

        left_percentage = values.get(left_value, 0)
        right_percentage = values.get(right_value, 0)

        # Determine slider value based on the right criteria
        slider_value = right_percentage

    else:
        left_percentage = 0
        right_percentage = 0
        slider_value = 0

    # Add each item as a grid item inside the outer grid
    col = columns[i % 3]
    with col:
        st.markdown(f"<div class='grid-item'><span>{left_value}</span><div class='slider-container'><input type='range' min='0' max='100' value='{slider_value}' class='slider' disabled></div><span>{right_value}</span></div>", unsafe_allow_html=True)


# Add space between Row B and Row C
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Display the user's statistics by popularity, decade, and length of the songs
col1, col2, col3 = st.columns([5, 5, 5])

# By popularity

with col1:

    # Categorize the tracks based on popularity
    df['popularity_category'] = df['popularity'].apply(
        lambda x: 'Popular' if x >= 70 else 'Average' if x >= 40 else 'Obscure'
    )
    
    # Calculate the total minutes listened to for each category
    df['minutes_listened'] = df['duration_ms'] / 60000
    category_minutes = df.groupby('popularity_category')['minutes_listened'].sum()
    
    # Calculate the percentage of minutes listened to for each category
    total_minutes = category_minutes.sum()
    category_percentages = (category_minutes / total_minutes) * 100
    
    # Get the most popular and most obscure songs
    most_popular_song = df[df['popularity_category'] == 'Popular'].iloc[0]
    most_obscure_song = df[df['popularity_category'] == 'Obscure'].iloc[0]
    
    # Display the popularity statistics
    st.markdown(
        f"""
        <style>
        .label {{
            color: white;
            font-weight: 600;
            margin-left: 30px;
            font-size: 15px;
            width:100%;
        }}
        progress[value] {{
            /* Reset the default appearance */
            -webkit-appearance: none;
            appearance: none;
            height: 10px;
            margin-right: 50px;
            width: 200%;
        }}
        progress[value]::-webkit-progress-bar {{
            background-color: #14171d;
            border-radius: 10px;
            overflow: hidden;
            
        }}
        progress[value]::-webkit-progress-value {{
            background-color: #1DB954;
            border-radius: 10px;
        }}
        progress[value]::-moz-progress-bar {{
            background-color: #1DB954;
            border-radius: 10px;
        }}
        </style>
        <div style="background-color: #14171d; padding: 15px; border-radius: 10px; height: auto;"> 
            <h5 style="color: white; margin-right: 20px; font-size:30px; margin-bottom: 10px; margin-top: 10px; font-weight:800; margin-left: 10px;">By Popularity</h5>
            <div style="background-color: #14171d; display:flex; align-items: center;">
                <p class="label" style="margin-bottom: 0;">Obscure</p>
                <progress value="{category_percentages['Obscure']}" max="100"></progress>
            </div>
            <div style="background-color: #14171d; display:flex; align-items: center;">
                <p class="label" style="margin-bottom: 0;">Average</p>
                <progress value="{category_percentages['Average']}" max="100"></progress>
            </div>
            <div style="background-color: #14171d; display:flex; align-items: center;">
                <p class="label" style="margin-bottom: 0;">Popular</p>
                <progress value="{category_percentages['Popular']}" max="100"></progress>
            </div>
            <h5 style="color: white; margin-right: 20px; font-size:20px; margin-top: 30px; font-weight:800; margin-left: 10px;">Most Popular</h5>
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                <img src="{most_popular_song['album_image_url']}" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">
                <div style="flex-grow: 1;">
                    <p style="color: white; margin-bottom: 2px;">{most_popular_song['track_name']}</p>
                    <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{most_popular_song['artist_name']}</p>
                </div>
            </div>
            <h5 style="color: white; margin-right: 20px; font-size:20px; margin-top: 30px; font-weight:800; margin-left: 10px;">Most Obscure</h5>
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                <img src="{most_obscure_song['album_image_url']}" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">
                <div style="flex-grow: 1;">
                    <p style="color: white; margin-bottom: 2px;">{most_obscure_song['track_name']}</p>
                    <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{most_obscure_song['artist_name']}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# By Decade
with col2:
    # Extract the release year and calculate the decade
    df['release_year'] = df['track_id'].apply(lambda x: sp.track(x)['album']['release_date'][:4])
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df['decade'] = (df['release_year'] // 10) * 10

    # Calculate the total minutes listened to for each decade
    df['minutes_listened'] = df['track_id'].apply(lambda x: sp.track(x)['duration_ms'] / 60000)
    decade_minutes = df.groupby('decade')['minutes_listened'].sum()

    # Calculate the percentage of minutes listened to for each decade
    total_minutes = decade_minutes.sum()
    decade_percentages = (decade_minutes / total_minutes) * 100

    # Identify the newest and oldest songs
    newest_song = df.loc[df['release_year'].idxmax()]
    oldest_song = df.loc[df['release_year'].idxmin()]

    # Display the decade statistics
    st.markdown(
        f"""
        <style>
        .label {{
            color: white;
            font-weight: 600;
            margin-left: 30px;
            font-size: 15px;
            width:100%;
        }}
        progress[value] {{
            /* Reset the default appearance */
            -webkit-appearance: none;
            appearance: none;
            height: 10px;
            margin-right: 50px;
            width: 200%;
        }}
        progress[value]::-webkit-progress-bar {{
            background-color: #14171d;
            border-radius: 10px;
            overflow: hidden;
            
        }}
        progress[value]::-webkit-progress-value {{
            background-color: #1DB954;
            border-radius: 10px;
        }}
        progress[value]::-moz-progress-bar {{
            background-color: #1DB954;
            border-radius: 10px;
        }}
        </style>
        <div style="background-color: #14171d; padding: 15px; border-radius: 10px; height: auto;"> 
            <h5 style="color: white; margin-right: 20px; font-size:30px; margin-bottom: 10px; margin-top: 10px; font-weight:800; margin-left: 10px;">By Decade</h5>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sort the decades in descending order
    sorted_decade_percentages = dict(sorted(decade_percentages.items(), key=lambda item: item[0], reverse=True))

    for decade, percentage in sorted_decade_percentages.items():
        st.markdown(
            f"""
            <div style="background-color: #14171d; display:flex; align-items: center;">
                <p class="label">{decade}s</p>
                <progress value="{percentage}" max="100"></progress>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
            f"""
            <div style="background-color: #14171d;">
                <h5 style="color: white; margin-right: 20px; font-size:20px;  font-weight:800; margin-left: 10px;">Newest Song</h5>
                <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                    <img src="{newest_song['album_image_url']}" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">
                    <div style="flex-grow: 1;">
                        <p style="color: white; margin-bottom: 2px;">{newest_song['track_name']}</p>
                        <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{newest_song['artist_name']}</p>
                    </div>
                </div>
                <h5 style="color: white; margin-right: 20px; font-size:20px; margin-top: 30px; font-weight:800; margin-left: 10px;">Oldest Song</h5>
                <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                    <img src="{oldest_song['album_image_url']}" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">
                    <div style="flex-grow: 1;">
                        <p style="color: white; margin-bottom: 2px;">{oldest_song['track_name']}</p>
                        <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{oldest_song['artist_name']}</p>
                    </div>
                </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

#By Length
with col3:
    # Extract the duration of each track in minutes
    df['minutes_listened'] = df['duration_ms'] / 60000

    # Categorize the tracks based on their length
    df['length_category'] = df['minutes_listened'].apply(
        lambda x: '≤ 4m' if x <= 4 else '5–9m' if x <= 9 else '10–19m'
    )

    # Calculate the total minutes listened to for each length category
    length_minutes = df.groupby('length_category')['minutes_listened'].sum()

    # Calculate the percentage of minutes listened to for each category
    total_minutes = length_minutes.sum()
    length_percentages = (length_minutes / total_minutes) * 100

    # Identify the longest and shortest songs
    longest_song = df.loc[df['minutes_listened'].idxmax()]
    shortest_song = df.loc[df['minutes_listened'].idxmin()]

    # Display the length statistics
    st.markdown(
        f"""
        <style>
        .label {{
            color: white;
            font-weight: 600;
            margin-left: 30px;
            font-size: 15px;
            width:100%;
        }}
        progress[value] {{
            /* Reset the default appearance */
            -webkit-appearance: none;
            appearance: none;
            height: 10px;
            margin-right: 50px;
            width: 200%;
        }}
        progress[value]::-webkit-progress-bar {{
            background-color: #14171d;
            border-radius: 10px;
            overflow: hidden;
            
        }}
        progress[value]::-webkit-progress-value {{
            background-color: #1DB954;
            border-radius: 10px;
        }}
        progress[value]::-moz-progress-bar {{
            background-color: #1DB954;
            border-radius: 10px;
        }}
        </style>
        <div style="background-color: #14171d; padding: 15px; border-radius: 10px; height: auto;"> 
            <h5 style="color: white; margin-right: 20px; font-size:30px; margin-bottom: 10px; margin-top: 10px; font-weight:800; margin-left: 10px;">By Length 🎀</h5>
        """,
        unsafe_allow_html=True
    )

    for length, percentage in length_percentages.items():
        st.markdown(
            f"""
            <div style="background-color: #14171d; display:flex; align-items: center;">
                <p class="label">{length}</p>
                <progress value="{percentage}" max="100"></progress>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div style="background-color: #14171d; padding: 15px; border-radius: 5px;">
            <h5 style="color: white; margin-right: 20px; font-size:20px; margin-top: 30px; font-weight:800; margin-left: 10px;">Longest Song</h5>
            <div style="display: flex; align-items: center; height: 70px;"> 
                <img src="{longest_song['album_image_url']}" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">
                <div style="flex-grow: 1;">
                    <p style="color: white; margin-bottom: 2px;">{longest_song['track_name']}</p>
                    <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{longest_song['artist_name']}</p>
                </div>
            </div>
            <h5 style="color: white; margin-right: 20px; font-size:20px; margin-top: 30px; font-weight:800; margin-left: 10px;">Shortest Song</h5>
            <div style="display: flex; align-items: center; height: 70px;"> 
                <img src="{shortest_song['album_image_url']}" width="50" height="50" style="border-radius: 10%; margin-right: 10px; margin-bottom: 20px;">
                <div style="flex-grow: 1;">
                    <p style="color: white; margin-bottom: 2px;">{shortest_song['track_name']}</p>
                    <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{shortest_song['artist_name']}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Add space between Row C and Row D
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

#show user's playlists 
 
st.header("Playlists")
# Include Font Awesome CSS
st.markdown(
    """
    <style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    </style>
    """,
    unsafe_allow_html=True
)

# Get the user's playlists
playlists = sp.current_user_playlists(limit=50)

# Display the user's playlists

# Create a grid layout using Streamlit's columns
columns = st.columns(4)

# Loop through the playlists and add items to the grid
for i, playlist in enumerate(playlists['items']):
    playlist_image_url = playlist['images'][0]['url'] if playlist['images'] else None
    playlist_name = playlist['name']
    playlist_likes = playlist['owner']['followers']['total'] if 'followers' in playlist['owner'] else 0
    playlist_description = playlist['description'] if playlist['description'] else ''

    # Fetch the tracks for the current playlist
    playlist_tracks = sp.playlist_tracks(playlist_id=playlist['id'])

    # Calculate the total duration of the playlist in milliseconds
    playlist_duration_ms = 0
    for track in playlist_tracks['items']:
        if 'track' in track and track['track'] is not None:
            track_info = track['track']
            duration_ms = track_info.get('duration_ms', 0)
            playlist_duration_ms += duration_ms  # Sum in milliseconds

    # Convert the total duration to hours and minutes
    playlist_duration_hours = playlist_duration_ms // (1000 * 60 * 60)  # Convert to hours
    playlist_duration_minutes = (playlist_duration_ms // (1000 * 60)) % 60  # Get remaining minutes

    # Format the duration as "Xh Ym"
    if playlist_duration_hours > 0:
        formatted_duration = f"{playlist_duration_hours}h {playlist_duration_minutes}min"
    else:
        formatted_duration = f"{playlist_duration_minutes}min"




   
        # Add each item as a grid item inside the outer grid
    col = columns[i % 4]
    with col:
        st.markdown(
            f"""
            <div class="playlist-container"style="padding: 15px; border-radius: 5px; display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom:30px;">
                {'<img src="' + playlist_image_url + '" width="200" height="200" style="border-radius: 10%; margin-bottom: 10px;">' if playlist_image_url else ''}
                <p style="color: white; font-size: 20px; margin: 5px 0;font-weight:800px;">{playlist_name}</p>
                <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                    <div style="background-color: #14171d; border-radius: 20px; padding:  10px; display: flex; align-items: center;">
                        <p style="color: white;font-weight:600 ; font-size: 14px; margin: 0;padding:px;">{playlist_likes}</p>
                        <i class="fa fa-heart" style="color: white; opacity: 0.7; font-size: 14px; margin-left: 5px;"></i>
                    </div>
                    <div style="background-color: #14171d; border-radius: 20px; padding:  10px; display: flex; align-items: center;">
                        <p style="color: white;font-weight:600 ; font-size: 14px; margin: 0;padding:1px;">{formatted_duration}</p>
                        <i class="fa fa-clock" style="color: white; opacity: 0.7; font-size: 14px; margin-left: 5px;"></i>
                    </div>
                </div>
                <p style="color: white; opacity: 0.7; font-size: 15px; height: 30px; overflow: hidden;margin-top:5px; margin-bottom: 0;">{playlist_description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )




# Function to fetch recommendations with caching
def fetch_recommendations(session, seed_artists=None, limit=10):
    try:
        print("Fetching recommendations...")
        response = session.get(f"https://api.spotify.com/v1/recommendations?seed_artists={','.join(seed_artists)}&limit={limit}", headers={
            "Authorization": f"Bearer {sp.auth_manager.get_access_token(as_dict=False)}"
        })
        response.raise_for_status()
        results = response.json()
        recommendations = []

        for track in results['tracks']:
            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'url': track['external_urls']['spotify'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None
            }
            recommendations.append(track_info)

        print("Recommendations fetched successfully.")
        return recommendations
    except spotipy.exceptions.SpotifyException as e:
        st.error(f"An error occurred: {e}")
        print(f"SpotifyException: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        print(f"Exception: {e}")
        return []

# Fetch the user's top artists with caching
session = requests_cache.CachedSession()
try:
    response = session.get('https://api.spotify.com/v1/me/top/artists?limit=10', headers={
        "Authorization": f"Bearer {sp.auth_manager.get_access_token(as_dict=False)}"
    })
    response.raise_for_status()
    top_artists = response.json()
except spotipy.exceptions.SpotifyException as e:
    st.error(f"An error occurred while fetching top artists: {e}")
    print(f"SpotifyException: {e}")
except Exception as e:
    st.error(f"An unexpected error occurred while fetching top artists: {e}")
    print(f"Exception: {e}")

# Add custom CSS styling
st.markdown("""
    <style>
        .discover-new-music {
            color: red;
            text-align: center;
            padding: 20px;
            background-color: #14171d;
            border-radius: 5px;
        }
        .element-container {
            margin-bottom: 0px; /* Adjust this value to reduce space */
            padding-bottom: 0px; /* Adjust this value to reduce space */
        }
        .recommendation {
            background-color: #1DB954;
            padding: 10px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .recommendation img {
            border-radius: 5px;
            margin-right: 20px;
        }
        .recommendation p {
            margin: 0;
            color: black;
            font-weight: 700;
        }
        .stSelectbox div[data-baseweb="select"] > div:first-child {
            background-color: #191414;
            border-color: 	#1DB954;
        }
        .stSelectbox div[data-baseweb="select"] > div:first-child {
            background-color: #191414;
            border-color: 	#1DB954;
        }
        div.stButton > button:first-child {
            background-color: #14171d;
            color:white;
            font-size:20px;
            height:1.5em;
            width:15em;
            border-radius:10px 10px 10px 10px;
        }
        div.stButton > button:first-child:hover,
        div.stButton > button:first-child:active {
            border-color: #1DB954;
            text-decoration: underline;
            color: #1DB954; /* Corrected from text-color to color */
        }
        
    </style>
""", unsafe_allow_html=True)
st.subheader("𝄞 Discover New Music 𝄞")

# Initialize session state for selected artist and recommendations
if 'selected_artist' not in st.session_state:
    st.session_state.selected_artist = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

# Add a description
st.markdown("""
    You can discover new music by selecting an artist from your top artists list. We will recommend you some tracks based on that artist. 
    The recommendations may not necessarily be by that artist, but instead, we will recommend songs similar to that artist's songs.
""")

# Let the user choose an artist for recommendations
selected_artist = st.selectbox("Select an Artist for Recommendations:", [artist['name'] for artist in top_artists['items']])

# Update session state when an artist is selected
if selected_artist != st.session_state.selected_artist:
    st.session_state.selected_artist = selected_artist
    st.session_state.recommendations = None  # Reset recommendations when a new artist is selected

# Get the Spotify artist ID for the selected artist
artist_id = next((artist['id'] for artist in top_artists['items'] if artist['name'] == selected_artist), None) if selected_artist else None

# Fetch recommendations when the user clicks the button
if st.button("Get Recommendations"):
    print("Button clicked. Fetching recommendations...")
    if artist_id:
        st.session_state.recommendations = fetch_recommendations(session, seed_artists=[artist_id])
    else:
        st.session_state.recommendations = []   
        print("Recommendations fetched.")

    # Display the recommendations in two columns
    if st.session_state.recommendations:
        col1, col2 = st.columns(2)
        for i, rec in enumerate(st.session_state.recommendations):
            col = col1 if i % 2 == 0 else col2
            with col:
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style="background-color: #14171d;  border-radius: 5px; display: flex; align-items: center; height: 70px;"> 
                        <p style="color: white; opacity: 0.5; margin-left: 10px; font-weight:200; font-size:20px;">{i+1}</p>
                        <a href="{rec['url']}" target="_blank">
                            {'<img src="' + rec['image'] + '" width="50" height="50" style="border-radius: 10%; margin-left: 20px; margin-bottom: 10px;">' if rec['image'] else ''}
                        </a>
                        <div style="flex-grow:1 ;margin-left: 20px;">
                            <p style="color: white; margin-bottom: 2px;padding-top:10px;">{rec['name']} </p>
                            <p style="color: white; opacity: 0.5; font-weight:200; margin-top: 0;">{rec['artist']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.write("No recommendations found.")
        print("Recommendations displayed.")