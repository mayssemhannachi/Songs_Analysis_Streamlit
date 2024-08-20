import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
    scope="user-read-recently-played user-top-read user-read-playback-state",
    requests_timeout=30  # Increase the timeout to 30 seconds
))



# Page config
st.set_page_config(page_title='HarmonyHub', page_icon='🔗', layout='wide', initial_sidebar_state='expanded')

# Load the CSS file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Display the user's profile details
user = sp.current_user()
if user['images']:
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
col1, col2, col3 = st.columns([5, 2, 5])

# Add the header with the app name
with col1:
    st.title("HarmonyHub 🔗")

# Song playing
current_track = sp.current_playback()
if current_track:
    background_color = "#1DB954"  # You can change this to any color you prefer

    # Display the song's details
    with col3:
        st.markdown(f"""
            <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; display: flex; align-items: center;">
                <img src="{current_track['item']['album']['images'][0]['url']}" width="50" style="margin-right: 20px; border-radius:5px;">
                <div style="flex-grow: 1;">
                    <div style="display: flex; align-items: center;">
                        <p style="margin: 0; font: sans-serif; font-weight: 700;">{current_track['item']['name']}</p>
                        <div style="margin-right: 10px;">
                        </div>
                    </div>
                    <p style="margin: 0; color: black; font: sans-serif; font-weight: 700;">{current_track['item']['artists'][0]['name']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Add space between Row A and Row B
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 5])

# Display the user's top artists
with col1:
    st.header("Top Artists 🎤")
    top_artists = sp.current_user_top_artists(limit=10)

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
    # Display the top 5 artists' names
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
    st.header("Top Tracks 🎵")
    # Get the user's top tracks with the picture
    top_tracks = sp.current_user_top_tracks(limit=50)
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


# Extract user's most listened songs and store in a DataFrame
data = []

for track in top_tracks['items']:
    album = track['album']
    album_name = album['name']
    album_image_url = album['images'][0]['url'] if album['images'] else None
    artist_name = album['artists'][0]['name']
    genres = sp.artist(album['artists'][0]['id'])['genres']  # Get genres of the artist

    data.append({
        'track_name': track['name'],
        'album_name': album_name,
        'album_image_url': album_image_url,
        'artist_name': artist_name,
        'genres': genres
    })

df = pd.DataFrame(data)

# Count the number of songs listened to for each album
album_counts = df['album_name'].value_counts().reset_index()
album_counts.columns = ['album_name', 'count']

# Merge the counts with the original DataFrame to get album details
top_albums_df = pd.merge(album_counts, df.drop_duplicates(subset=['album_name']), on='album_name')

with col1:
    # Display the top albums
    st.header("Top Albums 📀")

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
    # Display the top genres
    st.header("Top Genres 🎶")

    # Get the top genres from the DataFrame
    genres = df.explode('genres')['genres'].value_counts().head(9)

    # Display the top genres
    for i, (genre, count) in enumerate(genres.items()):
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

#Extract user's last listened songs
recently_played = sp.current_user_recently_played(limit=50)
tracks = recently_played['items']

# Extract the user's top 50 tracks
data = []

for track in top_tracks['items']:
    track_id = track['id']
    track_features = sp.audio_features([track_id])[0]  # Get audio features of the track

    # Categorize the track based on audio features
    mood = 'Sad' if track_features['valence'] <= 0.5 else 'Happy'
    rhythm = 'Danceable' if track_features['danceability'] >= 0.5 else 'Unrhythmic'
    tempo = 'Fast' if track_features['tempo'] >= 120 else 'Slow'
    acoustic = 'Acoustic' if track_features['acousticness'] >= 0.5 else 'Electric'
    energy = 'Energetic' if track_features['energy'] >= 0.5 else 'Relaxing'
    loudness = 'Soft' if track_features['loudness'] >= -5 else 'Loud'
    instrumental = 'Instrumental' if track_features['instrumentalness'] >= 0.5 else 'With Vocals'
    live = 'Live' if track_features['liveness'] >= 0.5 else 'Studio'
    spoken = 'Spoken' if track_features['speechiness'] >= 0.5 else 'Musical'

    data.append({
        'track_name': track['name'],
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

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Debugging: Print the DataFrame columns to check if all expected columns are present
print("DataFrame columns:", df.columns)

# Debugging: Print the first few rows of the DataFrame to check the data
print(df.head(20))

# Calculate the percentage of each category
criteria = ['mood', 'rhythm', 'tempo', 'acoustic', 'energy', 'loudness', 'instrumental', 'live', 'spoken']

percentages = {}
for criterion in criteria:
    if criterion in df.columns:
        value_counts = df[criterion].value_counts(normalize=True) * 100
        percentages[criterion] = value_counts

# Create a DataFrame to display the percentages
percentages_df = pd.DataFrame(percentages).T

# List of all criteria
all_criteria = ['mood', 'rhythm', 'tempo', 'acoustic', 'energy', 'loudness', 'instrumental', 'live', 'spoken']

# Ensure all criteria are included in percentages_df with 0% if they are not present
for criterion in all_criteria:
    if criterion not in percentages_df.index:
        # Add criterion with 0% values for all categories
        percentages_df.loc[criterion] = pd.Series([0] * len(percentages_df.columns), index=percentages_df.columns)

# Adjust the column names for display purposes
percentages_df.columns = [f"{col}" for col in percentages_df.columns]

# Debugging: Print the DataFrame to check the data
print(percentages_df)


# Ensure all criteria are present in the DataFrame
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

# Add missing criteria with 0% values for all categories
for criterion in criteria_opposites.keys():
    if criterion not in percentages_df.columns:
        percentages_df[criterion] = pd.Series([0] * len(percentages_df.index), index=percentages_df.index)

# Adjust the column names for display purposes
percentages_df.columns = [f"{col}" for col in percentages_df.columns]

# Debugging: Print the DataFrame to check the data
print(percentages_df)

# Display the user's music taste statistics
st.header("Taste 🎧ྀི")



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
    # Fetch the most popular songs on Spotify
    top_spotify_tracks = sp.playlist_tracks('37i9dQZEVXbMDoHDwVN2tF', limit=50)  # Spotify Global Top 50 playlist
    top_spotify_track_ids = [track['track']['id'] for track in top_spotify_tracks['items']]

    # Extract user's most listened songs and store in a DataFrame
    data = []

    for track in top_tracks['items']:
        track_id = track['id']
        track_name = track['name']
        popularity = track['popularity']
        is_popular = track_id in top_spotify_track_ids

        data.append({
            'track_id': track_id,
            'track_name': track_name,
            'popularity': popularity,
            'is_popular': is_popular
        })

    df = pd.DataFrame(data)

    # Categorize the tracks based on popularity
    df['popularity_category'] = df['popularity'].apply(
        lambda x: 'Popular' if x >= 70 else 'Average' if x >= 40 else 'Obscure'
    )

    # Calculate the percentage of each category
    popularity_percentages = df['popularity_category'].value_counts(normalize=True) * 100
    
    # Display the popularity statistics
    st.markdown(
    f"""
    <div style="background-color: #14171d; padding: 15px; border-radius: 5px; gap:20px; height: auto;"> 
        <h5 style="color: white; margin-right: 20px; font-size:20px; margin: 0; font-weight:800;">By Popularity 🤩</h5>
        
        <h6 style="color: white; opacity: 0.5; margin-right: 20px; font-size:20px; margin: 0;">Popular</h6>
        <div style="background-color: #333; border-radius: 5px; overflow: hidden;">
            <progress value="{popularity_percentages['Popular']}" max="100" style="width: 100%; height: 20px; background-color: #444; color: #1DB954;"></progress>
        </div>
        
        <h6 style="color: white; opacity: 0.5; margin-right: 20px; font-size:20px; margin: 0;">Average</h6>
        <div style="background-color: #333; border-radius: 5px; overflow: hidden;">
            <progress value="{popularity_percentages['Average']}" max="100" style="width: 100%; height: 20px; background-color: #444; color: #1DB954;"></progress>
        </div>
        
        <h6 style="color: white; opacity: 0.5; margin-right: 20px; font-size:20px; margin: 0;">Obscure</h6>
        <div style="background-color: #333; border-radius: 5px; overflow: hidden;">
            <progress value="{popularity_percentages['Obscure']}" max="100" style="width: 100%; height: 20px; background-color: #444; color: #1DB954;"></progress>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

#By Decade
with col2:
    st.markdown(
            f"""
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; gap:20px;height: 70px;"> 
                <h5 style="color: white;  margin-right: 20px; font-size:20px; margin: 0;font-weight:800;">By Decade ⏳</h5>
            </div>
            """,
            unsafe_allow_html=True
        )

#By Length
with col3:
    st.markdown(
            f"""
            <div style="background-color: #14171d; padding: 15px; border-radius: 5px; display: flex; align-items: center; gap:20px;height: 70px;"> 
                <h5 style="color: white;  margin-right: 20px; font-size:20px; margin: 0;font-weight:800;">By Length 🎀</h5>
            </div>
            """,
            unsafe_allow_html=True
        )







