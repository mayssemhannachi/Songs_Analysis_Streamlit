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
    scope="user-read-recently-played user-top-read user-read-playback-state"
))

# Page config
st.set_page_config(page_title='Spotify Analysis', page_icon='🧸', layout='wide', initial_sidebar_state='expanded')

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
    st.image(profile_image_url, width=130)