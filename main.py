import os
import tempfile
import pyttsx3
from gtts import gTTS
import sys
import winsound
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QSlider, QComboBox, QFileDialog, QRadioButton, 
                           QHBoxLayout, QMessageBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QEasingCurve, QPropertyAnimation, QRect
from PyQt5.QtGui import QColor, QPalette, QFont
import shutil
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

class ModernButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)

class TextToSpeechApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize pyttsx3 engine once
        self.engine = pyttsx3.init()
        
        # Get available voices
        self.available_voices = self.engine.getProperty('voices')
        
        # Store voice options
        self.voice_options = {
            'male': None,
            'female': None,
            'default': self.available_voices[0] if self.available_voices else None
        }
        
        # Find and categorize voices
        for voice in self.available_voices:
            voice_name = voice.name.lower()
            if 'david' in voice_name or 'james' in voice_name or 'mark' in voice_name:
                self.voice_options['male'] = voice
            elif 'zira' in voice_name or 'heather' in voice_name or 'susan' in voice_name:
                self.voice_options['female'] = voice

        # Supported languages for gTTS
        self.supported_languages = {
            "English": "en", "Spanish": "es", "French": "fr", "German": "de",
            "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
            "Korean": "ko", "Chinese": "zh-cn"
        }

        # Create temp directory
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'tts_app')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize audio file path
        self.generated_audio_path = None
        
        # Set the application-wide style
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial;
                font-size: 20px;
            }
            
            QLabel {
                color: #cdd6f4;
                font-size: 20px;
                font-weight: bold;
                margin-top: 10px;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #313244;
                border-radius: 6px;
                background-color: #313244;
                color: #cdd6f4;
                margin: 5px 0;
            }
            
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
            
            ModernButton, QPushButton {
                background-color: #313244;
                border: none;
                border-radius: 6px;
                padding: 10px;
                color: #cdd6f4;
                font-weight: bold;
                margin: 5px 0;
            }
            
            ModernButton:hover, QPushButton:hover {
                background-color: #45475a;
            }
            
            ModernButton:pressed, QPushButton:pressed {
                background-color: #585b70;
            }
            
            #convertButton {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            
            #convertButton:hover {
                background-color: #b4befe;
            }
            
            #playButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
            }
            
            #playButton:hover {
                background-color: #94e2d5;
            }
            
            #downloadButton {
                background-color: #f38ba8;
                color: #1e1e2e;
            }
            
            #downloadButton:hover {
                background-color: #fab387;
            }
            
            QComboBox {
                padding: 8px;
                border: 2px solid #313244;
                border-radius: 6px;
                background-color: #313244;
                color: #cdd6f4;
                min-width: 100px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cdd6f4;
                margin-right: 8px;
            }
            
            QComboBox:on {
                border: 2px solid #89b4fa;
            }
            
            QComboBox QListView {
                background-color: #313244;
                border: none;
                padding: 4px;
                outline: none;
            }
            
            QComboBox QListView::item {
                padding: 4px;
                margin: 2px;
                border-radius: 4px;
            }
            
            QComboBox QListView::item:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
            }
            
            QRadioButton {
                spacing: 8px;
                color: #cdd6f4;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #313244;
                background-color: #1e1e2e;
            }
            
            QRadioButton::indicator:checked {
                background-color: #89b4fa;
                border: 2px solid #89b4fa;
            }
            
            QRadioButton::indicator:unchecked:hover {
                border: 2px solid #89b4fa;
            }
            
            QSlider::groove:horizontal {
                height: 4px;
                background: #313244;
                margin: 0 10px;
            }
            
            QSlider::handle:horizontal {
                background: #89b4fa;
                width: 18px;
                height: 18px;
                margin: -7px -9px;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #b4befe;
            }
            
            QProgressBar {
                border: none;
                background-color: #313244;
                border-radius: 6px;
                height: 12px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 6px;
            }
        """)
        
        self.initUI()

    def initUI(self):
        # Create main layout with padding
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Create a title label
        title_label = QLabel("VociFy : The Ultimate Text-to-Speech Conversion tool")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #89b4fa;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(title_label)

        # Voice selection section
        voice_frame = QFrame()
        voice_frame.setStyleSheet("QFrame { background-color: #313244; border-radius: 10px; padding: 10px; }")
        voice_layout = QVBoxLayout(voice_frame)

        voice_label = QLabel("Voice Type")
        voice_layout.addWidget(voice_label)

        voice_button_layout = QHBoxLayout()
        self.voice_male_radio = QRadioButton("Male")
        self.voice_female_radio = QRadioButton("Female")
        self.voice_male_radio.setChecked(True)
        voice_button_layout.addWidget(self.voice_male_radio)
        voice_button_layout.addWidget(self.voice_female_radio)
        voice_layout.addLayout(voice_button_layout)

        main_layout.addWidget(voice_frame)

        # Language selection
        self.language_label = QLabel("Language")
        main_layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox()
        for language in sorted(self.supported_languages.keys()):
            self.language_dropdown.addItem(language)
        self.language_dropdown.setCurrentText("English")
        main_layout.addWidget(self.language_dropdown)

        # Text input
        self.text_label = QLabel("Text Input")
        main_layout.addWidget(self.text_label)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type or paste your text here...")
        self.text_input.setMinimumHeight(40)
        main_layout.addWidget(self.text_input)

        # File upload button
        self.upload_pdf_button = ModernButton("Upload PDF")
        self.upload_pdf_button.clicked.connect(self.upload_pdf)
        main_layout.addWidget(self.upload_pdf_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Speech rate control
        self.rate_label = QLabel("Speech Rate")
        main_layout.addWidget(self.rate_label)

        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(150)
        self.rate_slider.setTickPosition(QSlider.TicksBelow)
        self.rate_slider.setTickInterval(25)
        main_layout.addWidget(self.rate_slider)

        # Action buttons
        self.convert_button = ModernButton("Convert to Speech")
        self.convert_button.setObjectName("convertButton")
        self.convert_button.clicked.connect(self.text_to_speech)
        main_layout.addWidget(self.convert_button)

        self.play_button = ModernButton("Play Audio")
        self.play_button.setObjectName("playButton")
        self.play_button.clicked.connect(self.play_audio)
        main_layout.addWidget(self.play_button)

        self.download_button = ModernButton("Download Audio")
        self.download_button.setObjectName("downloadButton")
        self.download_button.clicked.connect(self.download_audio)
        main_layout.addWidget(self.download_button)

        # Set the main layout
        self.setLayout(main_layout)
        
        # Window properties
        self.setWindowTitle("VoxiFy - Text to Speech Converter")
        self.setGeometry(300, 300, 500, 700)
        self.setMinimumWidth(400)

    def update_voice_status(self):
        """Update the status of available voices"""
        status = []
        if self.voice_options['male']:
            status.append(f"Male Voice: {self.voice_options['male'].name}")
        else:
            status.append("Male Voice: Not available")
            
        if self.voice_options['female']:
            status.append(f"Female Voice: {self.voice_options['female'].name}")
        else:
            status.append("Female Voice: Not available")
            
        status.append(f"Default Voice: {self.voice_options['default'].name}")
        
        QMessageBox.information(self, "Voice Status", "\n".join(status))

    def text_to_speech(self):
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Input Error", "Please enter some text to convert.")
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Get selected voice type
            voice_type = 'male' if self.voice_male_radio.isChecked() else 'female'
            
            # If selected voice is not available, use default
            if not self.voice_options[voice_type]:
                msg = f"Selected {voice_type} voice is not available. Using default voice: {self.voice_options['default'].name}"
                QMessageBox.warning(self, "Voice Selection", msg)
            
            # Set the voice
            voice = self.voice_options[voice_type] or self.voice_options['default']
            self.engine.setProperty('voice', voice.id)
            
            # Set the rate
            rate = self.rate_slider.value()
            self.engine.setProperty('rate', rate)

            # Generate speech
            output_wav = os.path.join(self.temp_dir, 'output.wav')
            self.progress_bar.setValue(30)
            
            self.engine.save_to_file(text, output_wav)
            self.engine.runAndWait()
            
            self.progress_bar.setValue(70)
            
            if os.path.exists(output_wav):
                self.generated_audio_path = output_wav
                self.progress_bar.setValue(100)
                QMessageBox.information(self, "Success", "Text converted to speech successfully!")
            else:
                raise Exception("Failed to generate audio file")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def play_audio(self):
        try:
            if self.generated_audio_path and os.path.exists(self.generated_audio_path):
                winsound.PlaySound(self.generated_audio_path, winsound.SND_FILENAME)
            else:
                QMessageBox.warning(self, "Playback Error", "No audio file available. Please convert text first.")
        except Exception as e:
            QMessageBox.critical(self, "Playback Error", f"Error playing audio: {str(e)}")

    def download_audio(self):
        if not self.generated_audio_path or not os.path.exists(self.generated_audio_path):
            QMessageBox.warning(self, "Download Error", "No audio available to download. Please convert text first.")
            return

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Audio File",
                os.path.expanduser("~/Downloads/audio.wav"),
                "WAV Files (*.wav)"
            )

            if file_path:
                shutil.copy2(self.generated_audio_path, file_path)
                QMessageBox.information(self, "Success", f"Audio saved successfully to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save audio file: {str(e)}")

    def upload_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                # Extract text from PDF
                extracted_text = self.extract_text_from_pdf(file_path)
                if extracted_text:
                    self.text_input.setText(extracted_text)
                    QMessageBox.information(self, "PDF Text Extraction", "Text extracted successfully from the PDF.")
                else:
                    QMessageBox.warning(self, "PDF Error", "No text found in the PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to extract text from the PDF: {str(e)}")

    def extract_text_from_pdf(self, pdf_path):
        try:
            # Read PDF content
            with open(pdf_path, "rb") as file:
                reader = PdfReader(file)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text()
                return pdf_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def closeEvent(self, event):
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
        super().closeEvent(event)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for better dark theme compatibility
        window = TextToSpeechApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {str(e)}")
