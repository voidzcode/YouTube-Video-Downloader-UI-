import os
import threading
import customtkinter as ctk
from yt_dlp import YoutubeDL

# Set modern visual styling
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YoutubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Modern YouTube Downloader")
        self.geometry("580x480")
        self.resizable(False, False)
        
        # --- UI LAYOUT ELEMENTS ---
        # Header Title
        self.header_label = ctk.CTkLabel(self, text="YouTube Downloader Engine", font=ctk.CTkFont(size=22, weight="bold"))
        self.header_label.pack(padx=20, pady=20)
        
        # URL Input Box
        self.url_entry = ctk.CTkEntry(self, width=450, placeholder_text="Paste your YouTube video URL link here...")
        self.url_entry.pack(padx=20, pady=10)
        
        # Configuration Frame
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(padx=20, pady=15, fill="x")
        
        # Mode Selection Menu
        self.mode_label = ctk.CTkLabel(self.config_frame, text="Download Mode:", font=ctk.CTkFont(weight="bold"))
        self.mode_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.mode_menu = ctk.CTkOptionMenu(self.config_frame, values=["Video Only (MP4)", "Audio Only (MP3)", "Both (MP4 + MP3)"], command=self.toggle_menus)
        self.mode_menu.grid(row=0, column=1, padx=15, pady=10)
        
        # Resolution Menu
        self.res_label = ctk.CTkLabel(self.config_frame, text="Video Resolution:", font=ctk.CTkFont(weight="bold"))
        self.res_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.res_menu = ctk.CTkOptionMenu(self.config_frame, values=["Best Available", "1080p (Full HD)", "720p (HD)", "480p (SD)"])
        self.res_menu.grid(row=1, column=1, padx=15, pady=10)
        
        # Audio Quality Menu
        self.audio_label = ctk.CTkLabel(self.config_frame, text="Audio Quality:", font=ctk.CTkFont(weight="bold"))
        self.audio_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.audio_menu = ctk.CTkOptionMenu(self.config_frame, values=["320 kbps (Ultra)", "256 kbps (High)", "192 kbps (Standard)", "128 kbps (Low)"])
        self.audio_menu.grid(row=2, column=1, padx=15, pady=10)
        
        # Progress Bar & Output Status Status
        self.status_label = ctk.CTkLabel(self, text="Ready to process your request.", font=ctk.CTkFont(size=12))
        self.status_label.pack(padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=5)
        
        # Launch Download Action Button
        self.download_btn = ctk.CTkButton(self, text="Start Download Process", font=ctk.CTkFont(weight="bold"), width=200, height=40, command=self.start_download_thread)
        self.download_btn.pack(padx=20, pady=25)
        
        # Initial UI state sync
        self.toggle_menus(self.mode_menu.get())

    def toggle_menus(self, selected_mode):
        """Disables menus that are not required for specific workflows."""
        if "Audio Only" in selected_mode:
            self.res_menu.configure(state="disabled")
            self.audio_menu.configure(state="normal")
        elif "Video Only" in selected_mode:
            self.res_menu.configure(state="normal")
            self.audio_menu.configure(state="disabled")
        else:
            self.res_menu.configure(state="normal")
            self.audio_menu.configure(state="normal")

    def start_download_thread(self):
        """Spawns an independent workflow thread to keep the GUI responsive."""
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="❌ Please paste a valid URL first!")
            return
            
        self.download_btn.configure(state="disabled")
        self.status_label.configure(text="Connecting to engine server... ⏳")
        self.progress_bar.set(0.2)
        
        # Run execution loop on back-thread
        threading.Thread(target=self.execute_download, args=(url,), daemon=True).start()

    def execute_download(self, url):
        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        mode = self.mode_menu.get()
        res_choice = self.res_menu.get()
        audio_choice = self.audio_menu.get()
        
        # Format mapping configuration strings
        video_format = 'bestvideo'
        if "1080p" in res_choice: video_format = 'bestvideo[height<=1080]'
        elif "720p" in res_choice: video_format = 'bestvideo[height<=720]'
        elif "480p" in res_choice: video_format = 'bestvideo[height<=480]'
        
        audio_quality = "192"
        if "320" in audio_choice: audio_quality = "320"
        elif "256" in audio_choice: audio_quality = "256"
        elif "128" in audio_choice: audio_quality = "128"
        
        ydl_opts = {
            'noplaylist': True,
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'prefer_ffmpeg': True,
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
        }
        
        if "Video Only" in mode:
            ydl_opts['format'] = f'{video_format}+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif "Audio Only" in mode:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': audio_quality
            }]
        elif "Both" in mode:
            ydl_opts['format'] = f'{video_format}+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['keepvideo'] = True
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': audio_quality
            })
            
        try:
            self.progress_bar.set(0.5)
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Update GUI states upon success
            self.status_label.configure(text="✅ Complete! Files exported to your Downloads folder.")
            self.progress_bar.set(1.0)
        except Exception as e:
            self.status_label.configure(text=f"❌ Error encountered: {str(e)[:40]}...")
            self.progress_bar.set(0)
        finally:
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()
