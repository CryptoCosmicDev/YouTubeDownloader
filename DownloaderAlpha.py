import os
from pytube import YouTube, Playlist
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QComboBox, QFileDialog, QInputDialog, QHBoxLayout
)
from PyQt5.QtGui import QIcon


class YouTubeDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Set up the basic GUI elements
        self.setWindowTitle("YouTube Downloader")
        self.setWindowIcon(QIcon('screenshots/1384060.png'))  # Provide the path to your icon file

        # Create labels, input fields, buttons, and layout
        self.url_label = QLabel("Enter YouTube URL:")
        self.url_input = QLineEdit()

        self.output_label = QLabel("Select download location:")
        self.output_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.setToolTip("Browse for download location")
        self.browse_button.clicked.connect(self.browse_folder)

        self.resolution_label = QLabel("Select preferred resolution:")
        self.resolution_dropdown = QComboBox()

        self.download_button = QPushButton("Download")
        self.download_button.setToolTip("Start downloading")
        self.download_button.clicked.connect(self.download)

        self.layout = QVBoxLayout()
        self.setup_ui()

        # Display status messages
        self.status_label = QLabel()
        self.layout.addWidget(self.status_label)

    def setup_ui(self):
        # Arrange the GUI elements in a vertical layout
        self.layout.addWidget(self.url_label)
        self.layout.addWidget(self.url_input)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.browse_button)
        self.layout.addLayout(output_layout)

        self.layout.addWidget(self.resolution_label)
        self.layout.addWidget(self.resolution_dropdown)
        self.layout.addWidget(self.download_button)

        # Populate resolution dropdown with common resolutions
        resolutions = ["", "144p", "240p", "360p", "480p", "720p", "1080p"]
        self.resolution_dropdown.addItems(resolutions)

        self.setLayout(self.layout)

    def browse_folder(self):
        # Open a dialog to select the download folder
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        self.output_input.setText(folder)

    def display_available_formats(self, video):
        # Clear the dropdown and add an empty option
        self.resolution_dropdown.clear()
        self.resolution_dropdown.addItem("")  

        # Add available video resolutions to the dropdown
        for stream in video.streams:
            self.resolution_dropdown.addItem(f"{stream.resolution} - {stream.mime_type}")

    def download(self):
        # Get input values
        url = self.url_input.text()
        output_path = self.output_input.text()
        resolution = self.resolution_dropdown.currentText()

        # Check if it's a playlist
        if 'playlist' in url.lower():
            self.download_playlist(url, output_path, resolution)
        else:
            yt = YouTube(url)
            self.display_available_formats(yt)

            # If resolution is specified, download the video; otherwise, ask the user
            if resolution:
                self.download_video(yt, output_path, resolution)
            else:
                resolution = self.show_resolution_dialog(yt)
                if resolution:
                    self.download_video(yt, output_path, resolution)

    def download_video(self, yt, output_path, resolution):
        try:
            # Find the selected video stream
            video = yt.streams.filter(res=resolution).first()

            if video:
                # Display status, download the video, and show completion message
                self.status_label.setText(f"Downloading: {yt.title} - {video.resolution}")
                video.download(output_path)
                self.status_label.setText("Download complete.")
            else:
                # If no video available in the specified resolution, show a message
                self.status_label.setText(f"No video available in the specified resolution.")

        except Exception as e:
            # Display an error message if an exception occurs
            self.status_label.setText(f"An error occurred: {e}")

    def download_playlist(self, url, output_path, resolution):
        try:
            # Download videos from a playlist
            playlist = Playlist(url)
            playlist_folder = os.path.join(output_path, playlist.title)
            os.makedirs(playlist_folder, exist_ok=True)

            # Display playlist download status
            self.status_label.setText(f"Downloading playlist: {playlist.title}")

            for video_url in playlist.video_urls:
                yt = YouTube(video_url)
                self.display_available_formats(yt)

                # If resolution is specified, download the video; otherwise, ask the user
                if resolution:
                    self.download_video(yt, playlist_folder, resolution)
                else:
                    resolution = self.show_resolution_dialog(yt)
                    if resolution:
                        self.download_video(yt, playlist_folder, resolution)

            # Display completion message for playlist download
            self.status_label.setText("Playlist download complete. All videos are saved in the playlist folder.")
        except Exception as e:
            # Display an error message if an exception occurs during playlist download
            self.status_label.setText(f"An error occurred: {e}")

    def show_resolution_dialog(self, yt):
        # Display a dialog to choose the video resolution
        resolutions = [stream.resolution for stream in yt.streams]
        resolution, ok = QInputDialog.getItem(
            self, "Select Resolution", "Choose the resolution:", resolutions, 0, False
        )
        if ok and resolution:
            return resolution.split()[0]  # Extract resolution (e.g., "720p" from "720p - video/mp4")

        return None


if __name__ == '__main__':
    app = QApplication([])
    window = YouTubeDownloaderGUI()
    window.setFixedWidth(600)  # Set a fixed width for the window
    window.setWindowTitle("YouTube Downloader")
    window.show()
    app.exec_()
