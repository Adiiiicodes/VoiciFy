import os
import tempfile
import pyttsx3
from gtts import gTTS
import sys
import winsound
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QComboBox, QFileDialog, QRadioButton, QHBoxLayout, QMessageBox, QProgressBar
from PyQt5.QtCore import Qt
from pydub import AudioSegment
import shutil
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import io

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
        
        # Set up the GUI layout
        self.initUI()
        
        # Show initial voice status
        self.update_voice_status()

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

    def initUI(self):
        layout = QVBoxLayout()

        # Voice selection
        self.voice_label = QLabel("Select Voice Type:")
        layout.addWidget(self.voice_label)

        self.voice_male_radio = QRadioButton("Male")
        self.voice_female_radio = QRadioButton("Female")
        self.voice_male_radio.setChecked(True)

        voice_layout = QHBoxLayout()
        voice_layout.addWidget(self.voice_male_radio)
        voice_layout.addWidget(self.voice_female_radio)
        layout.addLayout(voice_layout)

        # Add voice info button
        self.voice_info_button = QPushButton("Voice Information")
        self.voice_info_button.clicked.connect(self.update_voice_status)
        layout.addWidget(self.voice_info_button)

        # Language selection
        self.language_label = QLabel("Select Language:")
        layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox(self)
        for language in sorted(self.supported_languages.keys()):
            self.language_dropdown.addItem(language)
        self.language_dropdown.setCurrentText("English")
        layout.addWidget(self.language_dropdown)

        # Text input
        self.text_label = QLabel("Enter Text:")
        layout.addWidget(self.text_label)

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Type your text here...")
        layout.addWidget(self.text_input)

        # Upload PDF button
        self.upload_pdf_button = QPushButton("Upload PDF")
        self.upload_pdf_button.clicked.connect(self.upload_pdf)
        layout.addWidget(self.upload_pdf_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Speech rate slider
        self.rate_label = QLabel("Speech Rate (Slower ⟷ Faster):")
        layout.addWidget(self.rate_label)

        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(150)
        self.rate_slider.setTickPosition(QSlider.TicksBelow)
        self.rate_slider.setTickInterval(25)
        layout.addWidget(self.rate_slider)

        # Buttons
        self.convert_button = QPushButton("Convert to Speech")
        self.convert_button.clicked.connect(self.text_to_speech)
        self.convert_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 5px; }")
        layout.addWidget(self.convert_button)

        self.play_button = QPushButton("Play Audio")
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setStyleSheet("QPushButton { background-color: #008CBA; color: white; padding: 5px; }")
        layout.addWidget(self.play_button)

        self.download_button = QPushButton("Download Audio")
        self.download_button.clicked.connect(self.download_audio)
        self.download_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 5px; }")
        layout.addWidget(self.download_button)

        # Set layout and window properties
        self.setLayout(layout)
        self.setWindowTitle("VoxiFy - Text to Speech Converter")
        self.setGeometry(300, 300, 400, 450)
        self.setStyleSheet("QWidget { background-color: #f0f0f0; }")

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

    def closeEvent(self, event):
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
        super().closeEvent(event)

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


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = TextToSpeechApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {str(e)}")
