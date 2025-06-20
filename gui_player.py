import os
import sys
import json
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import numpy as np
import sounddevice as sd
import threading
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

pygame.mixer.init()

class MusicPlayer:
    def __init__(self, root, username):
        self.root = root
        self.root.geometry("600x630")
        self.username = username
        self.root.title(f"{username}'s Music Player")

        self.is_paused = False
        self.is_playing = False
        self.shuffle = False
        self.current_index = 0
        self.playlist = []
        self.theme = "dark"
        self.visualizer_active = True
        self.track_length = 0

        self.playlist_file = f"data/{self.username}_playlist.json"
        self.load_playlist()
        self.setup_gui()
        self.apply_theme()

    def setup_gui(self):
        # Theme button at top-right
        self.theme_button = tk.Button(self.root, text="🌗 Theme", command=self.toggle_theme)
        self.theme_button.place(x=520, y=10, width=70, height=30)

        self.playlist_box = tk.Listbox(self.root, width=60)
        self.playlist_box.pack(pady=(50, 10))

        for song_path in self.playlist:
            self.playlist_box.insert(tk.END, os.path.basename(song_path))

        control_frame = tk.Frame(self.root)
        control_frame.pack()

        tk.Button(control_frame, text="▶ Play", width=10, command=self.play_music).grid(row=0, column=0)
        tk.Button(control_frame, text="⏸ Pause", width=10, command=self.pause_music).grid(row=0, column=1)
        tk.Button(control_frame, text="⏹ Stop", width=10, command=self.stop_music).grid(row=0, column=2)

        tk.Button(control_frame, text="⏮ Prev", width=10, command=self.prev_music).grid(row=1, column=0)
        tk.Button(control_frame, text="⏭ Next", width=10, command=self.next_music).grid(row=1, column=1)
        tk.Button(control_frame, text="🔀 Shuffle", width=10, command=self.toggle_shuffle).grid(row=1, column=2)

        self.volume_slider = ttk.Scale(self.root, from_=0, to=1, orient='horizontal', value=0.7, command=self.set_volume)
        self.volume_slider.pack(pady=10)
        pygame.mixer.music.set_volume(0.7)

        self.add_button = tk.Button(self.root, text="+ Add Songs", command=self.add_songs)
        self.add_button.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=580, height=150, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.bars = [self.canvas.create_rectangle(x * 14, 150, x * 14 + 10, 150, fill="lime") for x in range(40)]

    def apply_theme(self):
        if self.theme == "dark":
            bg = "black"
            fg = "lime"
            btn_bg = "#222"
            btn_fg = "white"
        else:
            bg = "white"
            fg = "darkblue"
            btn_bg = "#eee"
            btn_fg = "black"

        self.root.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.playlist_box.configure(bg=bg, fg=fg, selectbackground="gray")

        # Update themed buttons
        self.theme_button.configure(bg=btn_bg, fg=btn_fg)
        self.add_button.configure(bg=btn_bg, fg=btn_fg)

        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.configure(bg=btn_bg, fg=btn_fg)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    def add_songs(self):
        files = filedialog.askopenfilenames(title="Choose Audio Files", filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav")])
        for file in files:
            self.playlist.append(file)
            self.playlist_box.insert(tk.END, os.path.basename(file))
        self.save_playlist()

    def get_track_length(self, path):
        if path.endswith(".mp3"):
            return MP3(path).info.length
        elif path.endswith(".wav"):
            return WAVE(path).info.length
        return 0

    def update_progress_bar(self):
        if not self.is_playing or self.track_length == 0:
            return
        current_pos = pygame.mixer.music.get_pos() / 1000
        percent = (current_pos / self.track_length) * 100
        self.progress["value"] = percent
        if self.is_playing:
            self.root.after(500, self.update_progress_bar)

    def play_music(self):
        if not self.playlist:
            messagebox.showwarning("No Songs", "Please add some songs first!")
            return

        song = self.playlist[self.current_index]
        self.track_length = self.get_track_length(song)
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        self.playlist_box.select_clear(0, tk.END)
        self.playlist_box.select_set(self.current_index)
        self.is_playing = True
        self.is_paused = False
        self.visualizer_active = True

        self.progress["value"] = 0
        self.update_progress_bar()

        threading.Thread(target=self.fft_visualizer, daemon=True).start()

    def pause_music(self):
        if pygame.mixer.music.get_busy():
            if not self.is_paused:
                pygame.mixer.music.pause()
                self.visualizer_active = False
                self.is_paused = True
            else:
                pygame.mixer.music.unpause()
                self.visualizer_active = True
                threading.Thread(target=self.fft_visualizer, daemon=True).start()
                self.update_progress_bar()
                self.is_paused = False

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.visualizer_active = False
        self.progress["value"] = 0

    def next_music(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_music()

    def prev_music(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_music()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        messagebox.showinfo("Shuffle", "On" if self.shuffle else "Off")

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def load_playlist(self):
        os.makedirs("data", exist_ok=True)
        if os.path.exists(self.playlist_file):
            with open(self.playlist_file, "r") as f:
                self.playlist = json.load(f)

    def save_playlist(self):
        with open(self.playlist_file, "w") as f:
            json.dump(self.playlist, f)

    def fft_visualizer(self):
        def callback(indata, frames, time, status):
            if not self.visualizer_active or not self.is_playing:
                return
            audio_data = np.abs(np.fft.rfft(indata[:, 0]))
            audio_data = audio_data[:40]
            max_val = np.max(audio_data) + 1
            normalized = (audio_data / max_val) * 140
            for i, bar in enumerate(self.bars):
                height = int(normalized[i])
                self.canvas.coords(bar, i * 14, 150 - height, i * 14 + 10, 150)

        try:
            with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=1024):
                while self.visualizer_active and self.is_playing:
                    sd.sleep(50)
        except Exception as e:
            print("Visualizer error:", e)

# Run App
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python gui_player.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    print(f"Launching music player for: {username}")
    root = tk.Tk()
    app = MusicPlayer(root, username)
    root.mainloop()
