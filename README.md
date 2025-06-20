# 🎶 PyRetroMusicPlayer

**Retro themed music player application**

A desktop GUI-based retro music player built with Python using `Tkinter` for the interface, `pygame` for audio playback, and `Django` for user authentication. Designed for offline use, this app lets users log in, manage playlists, and enjoy local music with classic vibes.

---

## 🪄 Features

- 🔐 Django-based login & signup authentication (localhost)
- 🎧 Local music playback (MP3/WAV)
- ⏯️ Play, pause, next, previous track control
- 📂 Add and manage songs from local storage
- 🔀 Shuffle and 🔁 loop mode
- 🎚️ Volume control slider
- 🌓 Dark/light theme toggle
- 📈 Optional real-time FFT visualizer
- 🖥️ Offline usage — no internet required

---

## 🛠️ Installation & Run
```bash
# 1. Clone the Repository
git clone https://github.com/yourusername/PyRetroMusicPlayer.git
cd PyRetroMusicPlayer
# 2. (Optional) Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Requirements
pip install -r requirements.txt

# Make sure ffmpeg is installed and added to your system PATH if audio issues occur

# 4. Apply Django Migrations
cd music_player_project
python manage.py migrate

# 5. Create Superuser (Optional)
python manage.py createsuperuser

# 6. Run Django Authentication Server
python manage.py runserver

# Visit in browser to test:
# http://127.0.0.1:8000/signup/
# http://127.0.0.1:8000/login/

# 7. Launch the Music Player GUI (in a new terminal)
cd ..
python gui_app/main.py

# ---------------------------------------
# 📌 Requirements

# Python 3.8 or above
# Django 5+
# pygame
# Pillow
# ffmpeg (must be installed separately and added to PATH)

# To install all at once:
pip install -r requirements.txt
