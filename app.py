import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from streamlit_lottie import st_lottie
import requests

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
st.set_page_config(page_title='HarmonyHub', page_icon='🧸', layout='wide', initial_sidebar_state='expanded')

# Load the CSS file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to load Lottie animation from a URL
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()




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
col1, col2, col3= st.columns([5,2,5])

# Add the header with the app name
with col1:
    st.title("HarmonyHub 🧸")

# Song playing
current_track = sp.current_playback()
if current_track:
    background_color = "#1DB954"  # You can change this to any color you prefer

    # Load the Lottie animation
    lottie_animation = load_lottie_url("https://lottie.host/a8856bc8-09f5-41bb-ab5d-ce4797e1a6a9/bALctmN05s.json")

    # Display the song's details    
    
    with col3:
        st.markdown(f"""
            <div style="background-color: {background_color}; padding: 10px; border-radius: 5px; display: flex; align-items: center;">
                <img src="{current_track['item']['album']['images'][0]['url']}" width="50" style="margin-right: 10px;">
                <div style="flex-grow: 1;">
                    <p style="margin: 0;">{current_track['item']['name']}</p>
                    <p style="margin: 0; color: black;">{current_track['item']['artists'][0]['name']}</p>
                </div>
                <div id="lottie-container" style="width: 50px; height: 50px;">
                    <script src="https://unpkg.com/@dotlottie/player-component@latest/dist/dotlottie-player.mjs" type="module"></script> 

                <dotlottie-player src="https://lottie.host/a8856bc8-09f5-41bb-ab5d-ce4797e1a6a9/bALctmN05s.json" background="transparent" speed="1" style="width: 300px; height: 300px;" loop autoplay></dotlottie-player>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
       
    
    