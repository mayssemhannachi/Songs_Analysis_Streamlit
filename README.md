# HarmonyHub 🎵

HarmonyHub is a Streamlit application that allows users to connect their Spotify account and analyze their music preferences. Users can view their top tracks, recently played songs, and get personalized recommendations.

## Features

- Connect your Spotify account
- View your top tracks and artists
- See your recently played songs
- Get personalized song recommendations
- Analyze your listening habits by decade

## Setup

### Prerequisites

- Python 3.7 or higher
- Spotify Developer Account

### Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/your-username/harmonyhub.git
    cd harmonyhub
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up your Spotify Developer credentials**:
    - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and create a new application.
    - Add the redirect URI of your deployed app (e.g., `https://your-deployed-app-url`).
    - Copy the `Client ID` and `Client Secret`.

5. **Create a `.env` file in the root directory and add your Spotify credentials**:
    ```properties
    SPOTIPY_CLIENT_ID=your-client-id
    SPOTIPY_CLIENT_SECRET=your-client-secret
    SPOTIPY_REDIRECT_URI=https://your-deployed-app-url
    ```

## Usage

1. **Run the Streamlit app**:
    ```sh
    streamlit run app.py
    ```

2. **Open your browser and go to**:
    ```
    http://localhost:8501
    ```

3. **Authorize with Spotify**:
    - Click on the authorization link provided by the app.
    - Complete the authorization process.

4. **Explore your music preferences**:
    - View your top tracks and artists.
    - See your recently played songs.
    - Get personalized song recommendations.
    - Analyze your listening habits by decade.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Spotipy](https://spotipy.readthedocs.io/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)

## Contact

For any questions or feedback, please contact [h.mayssem2003@gmail.com](mailto:h.mayssem2003@gmail.com).