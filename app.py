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
    top_tracks = sp.current_user_top_tracks(limit=20)
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
top_tracks = sp.current_user_top_tracks(limit=50)
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

# Display the user's statistics based on their taste

# Extract the user's top 50 tracks
top_tracks = sp.current_user_top_tracks(limit=50)
data = []

for track in top_tracks['items']:
    track_id = track['id']
    track_features = sp.audio_features([track_id])[0]  # Get audio features of the track

    # Categorize the track based on audio features
    mood = 'Happy' if track_features['valence'] >= 0.5 else 'Sad'
    rhythm = 'Danceable' if track_features['danceability'] >= 0.5 else 'Unrhythmic'
    tempo = 'Fast' if track_features['tempo'] >= 120 else 'Slow'
    acoustic = 'Acoustic' if track_features['acousticness'] >= 0.5 else 'Electric'
    energy = 'Energetic' if track_features['energy'] >= 0.5 else 'Relaxing'
    loudness = 'Loud' if track_features['loudness'] >= -5 else 'Soft'
    instrumental = 'Instrumental' if track_features['instrumentalness'] >= 0.5 else 'With Vocals'
    live = 'Live' if track_features['liveness'] >= 0.5 else 'Studio'
    spoken = 'Musical' if track_features['speechiness'] >= 0.5 else 'Spoken'

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

#Debugging: Print the first few rows of the DataFrame to check the data
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

# Display the user's music taste statistics
st.header("Taste")

# Loop through criteria in sets of three
# Custom HTML and CSS for the grid layout
st.markdown(
    """
    <style>
    .outer-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr); /* 3 columns with equal width */
        gap: 20px; /* Space between outer grid items */
        padding: 20px;
        border-radius: 10px;
    }
    .grid-item {
        background-color: #14171d;
        border-radius: 5px;
        padding: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-weight: 800;
        font-size: 15px;
    }
    .progress-bar {
        background-color: #6e6e6e;
        height: 6px;
        border-radius: 5px;
        width: 150px;
        margin: 0 10px;
    }
    .progress-bar-inner {
        background-color: #1DB954;
        height: 6px;
        border-radius: 5px;
    }
    .container {
        margin: 50px; /* Add more space between container and text */
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Start the outer grid container
st.markdown('<div class="outer-grid">', unsafe_allow_html=True)

# Loop through the criteria and add items to the grid
for i in range(0, len(all_criteria)):
    criterion = all_criteria[i]
    if criterion in percentages_df.index:
        values = percentages_df.loc[criterion].dropna().sort_values(ascending=False)

        if len(values) == 0:
            value_1, percentage_1 = "N/A", 0
            value_2, percentage_2 = "N/A", 0
        elif len(values) == 1:
            value_1, percentage_1 = values.index[0], values.iloc[0]
            if value_1 == 'Spoken' and percentage_1 == 100:
                value_2, percentage_2 = 'Musical', 0
            else:
                value_2, percentage_2 = "N/A", 0
        else:
            if 'Spoken' in values.index and values.loc['Spoken'] == 100:
                value_1, percentage_1 = 'Spoken', 100
                value_2, percentage_2 = 'Musical', 0
            else:
                top_values = values.head(2)
                value_1, percentage_1 = top_values.index[0], top_values.iloc[0]
                value_2, percentage_2 = top_values.index[1], top_values.iloc[1]
    else:
        value_1, percentage_1 = "N/A", 0
        value_2, percentage_2 = "N/A", 0

    # Add each item as a grid item inside the outer grid
    st.markdown(
        f"""
        <div class="grid-item">
            <p>{value_1}</p>
            <div class="progress-bar">
                <div class="progress-bar-inner" style="width: {percentage_1}%;"></div>
            </div>
            <p>{value_2}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Close the outer grid container
st.markdown('</div>', unsafe_allow_html=True)


#Display user's statistics by popularity, Decade, and Lenghth of the songs

# Extract the user's top 50 tracks
top_tracks = sp.current_user_top_tracks(limit=50)
data = []

for track in top_tracks['items']:
    track_id = track['id']
    track_features = sp.audio_features([track_id])[0]  # Get audio features of the track

    # Categorize the track based on audio features
    popularity = 'Popular' if track['popularity'] >= 70 else 'Average' if track['popularity'] >= 30 else 'Obsecure'
    decade = 'Old' if track['album']['release_date'] < '2000' else 'Modern'
    length = 'Long' if track_features['duration_ms'] >= 240000 else 'Short'

    data.append({
        'track_name': track['name'],
        'popularity': popularity,
        'decade': decade,
        'length':all_ length
    })

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Debugging: Print the DataFrame columns to check if all expected columns are present
print("DataFrame columns:", df.columns)

# Debugging: Print the first few rows of the DataFrame to check the data
print(df.head(20))

# Calculate the percentage of each category
criteria = ['popularity', 'decade', 'length']

# Calculate the percentage of each decade
decade_counts = df['decade'].value_counts(normalize=True) * 100

# Add the percentage of each decade to the DataFrame
percentages['decade'] = decade_counts

# Create a DataFrame to display the percentages
percentages_df = pd.DataFrame(percentages).T

# Ensure all criteria are included in percentages_df with 0% if they are not present
for criterion in all_criteria:
    if criterion not in percentages_df.index:
        # Add criterion with 0% values for all categories
        percentages_df.loc[criterion] = pd.Series([0] * len(percentages_df.columns), index=percentages_df.columns)

# Adjust the column names for display purposes
percentages_df.columns = [f"{col}" for col in percentages_df.columns]

# Debugging: Print the DataFrame to check the data
print(percentages_df)