import os
import tempfile
import pyttsx3
from gtts import gTTS
import sys
import winsound
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QSlider, QComboBox, QFileDialog, QRadioButton, 
    QHBoxLayout, QMessageBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from pydub import AudioSegment
import shutil
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import io

class StyledFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            StyledFrame {
                background-color: black;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                
            }
        """)

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

        # Supported languages for gTTS with their codes
        self.supported_languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese (Simplified)": "zh-CN"
        }

        # Create temp directory
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'tts_app')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize audio file path
        self.generated_audio_path = None
        
        # Set up the GUI layout
        self.initUI()
        self.apply_styles()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Title with gradient effect
        title_label = QLabel("VoiciFy")
        title_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
                padding: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Text to Speech Converter")
        subtitle_label.setFont(QFont("Segoe UI", 14))
        subtitle_label.setStyleSheet("color: #BDC3C7;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Main content frame
        content_frame = StyledFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(15, 15, 15, 15)

        # Language selection
        lang_frame = StyledFrame()
        lang_layout = QVBoxLayout(lang_frame)
        
        self.language_label = QLabel("Select Language:")
        self.language_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.language_label.setStyleSheet("color: #ECF0F1;")
        lang_layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox()
        self.language_dropdown.setFont(QFont("Segoe UI", 10))
        for language in sorted(self.supported_languages.keys()):
            self.language_dropdown.addItem(language)
        self.language_dropdown.setCurrentText("English")
        self.language_dropdown.currentTextChanged.connect(self.on_language_change)
        lang_layout.addWidget(self.language_dropdown)
        
        content_layout.addWidget(lang_frame)

        # Voice selection frame
        voice_frame = StyledFrame()
        voice_layout = QVBoxLayout(voice_frame)
        
        self.voice_label = QLabel("Select Voice Type (English only):")
        self.voice_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.voice_label.setStyleSheet("color: #ECF0F1;")
        voice_layout.addWidget(self.voice_label)

        voice_options = QHBoxLayout()
        self.voice_male_radio = QRadioButton("Male")
        self.voice_female_radio = QRadioButton("Female")
        self.voice_male_radio.setChecked(True)
        voice_options.addWidget(self.voice_male_radio)
        voice_options.addWidget(self.voice_female_radio)
        voice_layout.addLayout(voice_options)
        
        content_layout.addWidget(voice_frame)

        # Text input frame
        text_frame = StyledFrame()
        text_layout = QVBoxLayout(text_frame)
        
        self.text_label = QLabel("Enter Text:")
        self.text_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.text_label.setStyleSheet("color: #ECF0F1;")
        text_layout.addWidget(self.text_label)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your text here...")
        self.text_input.setMinimumHeight(40)
        text_layout.addWidget(self.text_input)
        
        content_layout.addWidget(text_frame)

        # Upload PDF button
        self.upload_pdf_button = QPushButton("Upload PDF")
        self.upload_pdf_button.setMinimumHeight(45)
        content_layout.addWidget(self.upload_pdf_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        content_layout.addWidget(self.progress_bar)

        # Speech rate frame
        rate_frame = StyledFrame()
        rate_layout = QVBoxLayout(rate_frame)
        
        self.rate_label = QLabel("Speech Rate:")
        self.rate_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.rate_label.setStyleSheet("color: #ECF0F1;")
        rate_layout.addWidget(self.rate_label)

        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(150)
        self.rate_slider.setTickPosition(QSlider.TicksBelow)
        self.rate_slider.setTickInterval(25)
        rate_layout.addWidget(self.rate_slider)
        
        content_layout.addWidget(rate_frame)

        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.convert_button = QPushButton("Convert")
        self.play_button = QPushButton("Play")
        self.download_button = QPushButton("Download")
        
        for btn in [self.convert_button, self.play_button, self.download_button]:
            btn.setMinimumHeight(45)
            buttons_layout.addWidget(btn)

        content_layout.addLayout(buttons_layout)
        main_layout.addWidget(content_frame)

        # Connect button signals
        self.convert_button.clicked.connect(self.text_to_speech)
        self.play_button.clicked.connect(self.play_audio)
        self.download_button.clicked.connect(self.download_audio)
        self.upload_pdf_button.clicked.connect(self.upload_pdf)

        self.setLayout(main_layout)
        self.setWindowTitle("Voicify")
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)

    def apply_styles(self):
        # Set the application style
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A1A;
                color: #ECF0F1;
                height: 100px;
            }
            
            QLabel {
                color: #ECF0F1;
                font-size: 20x;
            }
            
            QComboBox {
                padding: 4px;
                border: 1px solid #34495E;
                border-radius: 5px;
                background-color: #2C3E50;
                color: #ECF0F1;
                height: 25px;
            }
            
            QComboBox::drop-down {
                border: none;
                padding: 0px 5px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ECF0F1;
            }
            
            QLineEdit {
                padding: 4px;
                border: 1px solid #34495E;
                border-radius: 5px;
                background-color: #2C3E50;
                color: #ECF0F1;
                selection-background-color: #3498DB;
                font-size: 16px;
            }
            
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px;
                font-weight: bold;
                font-size: 20px;
            }
            
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980B9, stop:1 #27AE60);
            }
            
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2475A8, stop:1 #229954);
            }
            
            QProgressBar {
                border: 1px solid #34495E;
                border-radius: 5px;
                text-align: center;
                color: #ECF0F1;
                background-color: #2C3E50;
            }
            
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
                border-radius: 5px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #34495E;
                height: 8px;
                background: #2C3E50;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498DB, stop:1 #2ECC71);
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QRadioButton {
                spacing: 8px;
                color: #ECF0F1;
            }
            
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #34495E;
            }
            
            QRadioButton::indicator:checked {
                background-color: #3498DB;
                border: 2px solid #2980B9;
            }
            
            QRadioButton::indicator:unchecked {
                background-color: #2C3E50;
                border: 2px solid #34495E;
            }
            
            QMessageBox {
                background-color: #1A1A1A;
                color: #ECF0F1;
            }
            
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 30px;
            
            }
        """)

   
    def on_language_change(self, language):
        """Handle language change events"""
        is_english = language == "English"
        self.voice_male_radio.setEnabled(is_english)
        self.voice_female_radio.setEnabled(is_english)
        self.rate_slider.setEnabled(is_english)
        self.voice_label.setText("Select Voice Type (English only):" if is_english else "Voice selection not available for non-English languages")
        self.rate_label.setText("Speech Rate:" if is_english else "Speech rate not adjustable for non-English languages")

        placeholder_texts = {
            "Russian": "Введите текст здесь...",
            "Chinese (Simplified)": "在这里输入文字...",
            "Japanese": "ここにテキストを入力してください...",
            "Korean": "여기에 텍스트를 입력하세요..."
        }
        self.text_input.setPlaceholderText(placeholder_texts.get(language, "Type your text here..."))

    def text_to_speech(self):
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Input Error", "Please enter some text to convert.")
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            selected_language = self.language_dropdown.currentText()
            lang_code = self.supported_languages[selected_language]
            
            temp_mp3 = os.path.join(self.temp_dir, 'temp.mp3')
            output_wav = os.path.join(self.temp_dir, 'output.wav')
            
            for file in [temp_mp3, output_wav]:
                if os.path.exists(file):
                    os.remove(file)
            
            self.progress_bar.setValue(20)

            if selected_language == "English":
                voice_type = 'male' if self.voice_male_radio.isChecked() else 'female'
                voice = self.voice_options[voice_type] or self.voice_options['default']
                self.engine.setProperty('voice', voice.id)
                self.engine.setProperty('rate', self.rate_slider.value())
                
                self.progress_bar.setValue(40)
                self.engine.save_to_file(text, output_wav)
                self.engine.runAndWait()
                self.progress_bar.setValue(80)
            else:
                try:
                    tts = gTTS(text=text, lang=lang_code, slow=False)
                    self.progress_bar.setValue(40)
                    
                    tts.save(temp_mp3)
                    self.progress_bar.setValue(60)
                    
                    audio = AudioSegment.from_mp3(temp_mp3)
                    audio.export(output_wav, format="wav")
                    self.progress_bar.setValue(80)
                    
                    if os.path.exists(temp_mp3):
                        os.remove(temp_mp3)
                except Exception as e:
                    raise Exception(f"gTTS error: {str(e)}")
            
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
                extracted_text = self.extract_text_from_pdf(file_path)
                if extracted_text:
                    self.text_input.setText(extracted_text)
                    QMessageBox.information(self, "Success", "Text extracted successfully from the PDF.")
                else:
                    QMessageBox.warning(self, "PDF Error", "No text found in the PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_pdf(self, pdf_path):
        try:
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
        app.setStyle('Fusion')  
        window = TextToSpeechApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {str(e)}")

        

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

        # Supported languages for gTTS with their codes
        self.supported_languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Japanese": "ja",
            "Korean": "ko",
            "Chinese (Simplified)": "zh-CN"
        }

        # Create temp directory
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'tts_app')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize audio file path
        self.generated_audio_path = None
        
        # Set up the GUI layout
        self.initUI()
        self.apply_styles()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("VoiciFy")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Text to Speech Converter")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)

        # Main content frame
        content_frame = StyledFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)
        

        # Language selection
        lang_frame = StyledFrame()
        lang_layout = QVBoxLayout(lang_frame)
        
        self.language_label = QLabel("Select Language:")
        self.language_label.setFont(QFont("Arial", 20, QFont.Bold))
        lang_layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox()
        self.language_dropdown.setFont(QFont("Arial", 10))
        for language in sorted(self.supported_languages.keys()):
            self.language_dropdown.addItem(language)
        self.language_dropdown.setCurrentText("English")
        self.language_dropdown.currentTextChanged.connect(self.on_language_change)
        lang_layout.addWidget(self.language_dropdown)
        
        content_layout.addWidget(lang_frame)

        # Voice selection frame
        voice_frame = StyledFrame()
        voice_layout = QVBoxLayout(voice_frame)
        
        self.voice_label = QLabel("Select Voice Type (English only):")
        self.voice_label.setFont(QFont("Arial", 10, QFont.Bold))
        voice_layout.addWidget(self.voice_label)

        voice_options = QHBoxLayout()
        self.voice_male_radio = QRadioButton("Male")
        self.voice_female_radio = QRadioButton("Female")
        self.voice_male_radio.setChecked(True)
        voice_options.addWidget(self.voice_male_radio)
        voice_options.addWidget(self.voice_female_radio)
        voice_layout.addLayout(voice_options)
        
        content_layout.addWidget(voice_frame)

        # Text input frame
        text_frame = StyledFrame()
        text_layout = QVBoxLayout(text_frame)
        
        self.text_label = QLabel("Enter Text:")
        self.text_label.setFont(QFont("Arial", 10, QFont.Bold))
        text_layout.addWidget(self.text_label)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your text here...")
        self.text_input.setMinimumHeight(40)
        text_layout.addWidget(self.text_input)
        
        content_layout.addWidget(text_frame)

        # Upload PDF button
        self.upload_pdf_button = QPushButton("Upload PDF")
        self.upload_pdf_button.setMinimumHeight(40)
        content_layout.addWidget(self.upload_pdf_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        content_layout.addWidget(self.progress_bar)

        # Speech rate frame
        rate_frame = StyledFrame()
        rate_layout = QVBoxLayout(rate_frame)
        
        self.rate_label = QLabel("Speech Rate:")
        self.rate_label.setFont(QFont("Arial", 10, QFont.Bold))
        rate_layout.addWidget(self.rate_label)

        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(150)
        self.rate_slider.setTickPosition(QSlider.TicksBelow)
        self.rate_slider.setTickInterval(25)
        rate_layout.addWidget(self.rate_slider)
        
        content_layout.addWidget(rate_frame)

        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.convert_button = QPushButton("Convert")
        self.play_button = QPushButton("Play")
        self.download_button = QPushButton("Download")
        
        for btn in [self.convert_button, self.play_button, self.download_button]:
            btn.setMinimumHeight(40)
            buttons_layout.addWidget(btn)

        content_layout.addLayout(buttons_layout)
        main_layout.addWidget(content_frame)

        # Connect button signals
        self.convert_button.clicked.connect(self.text_to_speech)
        self.play_button.clicked.connect(self.play_audio)
        self.download_button.clicked.connect(self.download_audio)
        self.upload_pdf_button.clicked.connect(self.upload_pdf)

        self.setLayout(main_layout)
        self.setWindowTitle("Voicify")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)

    def apply_styles(self):
        # Set the application style
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                color: #2f3640;
                height: 100px;
            }
            
            QLabel {
                color: #2f3640;
                font-size: 1px;
            }
            
            QComboBox {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 18px;
                
            }
            
            QLineEdit {
                padding: 4px;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 18px;
               
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                font-size: 20px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #2475a8;
            }
            
            QProgressBar {
                border: 1px solid #dcdde1;
                border-radius: 5px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #dcdde1;
                height: 8px;
                background: white;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #3498db;
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QRadioButton {
                spacing: 8px;
                font-size: 18px;
            }
            
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)

   
    def on_language_change(self, language):
        """Handle language change events"""
        is_english = language == "English"
        self.voice_male_radio.setEnabled(is_english)
        self.voice_female_radio.setEnabled(is_english)
        self.rate_slider.setEnabled(is_english)
        self.voice_label.setText("Select Voice Type (English only):" if is_english else "Voice selection not available for non-English languages")
        self.rate_label.setText("Speech Rate:" if is_english else "Speech rate not adjustable for non-English languages")

        placeholder_texts = {
            "Russian": "Введите текст здесь...",
            "Chinese (Simplified)": "在这里输入文字...",
            "Japanese": "ここにテキストを入力してください...",
            "Korean": "여기에 텍스트를 입력하세요..."
        }
        self.text_input.setPlaceholderText(placeholder_texts.get(language, "Type your text here..."))

    def text_to_speech(self):
        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Input Error", "Please enter some text to convert.")
            return

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            selected_language = self.language_dropdown.currentText()
            lang_code = self.supported_languages[selected_language]
            
            temp_mp3 = os.path.join(self.temp_dir, 'temp.mp3')
            output_wav = os.path.join(self.temp_dir, 'output.wav')
            
            for file in [temp_mp3, output_wav]:
                if os.path.exists(file):
                    os.remove(file)
            
            self.progress_bar.setValue(20)

            if selected_language == "English":
                voice_type = 'male' if self.voice_male_radio.isChecked() else 'female'
                voice = self.voice_options[voice_type] or self.voice_options['default']
                self.engine.setProperty('voice', voice.id)
                self.engine.setProperty('rate', self.rate_slider.value())
                
                self.progress_bar.setValue(40)
                self.engine.save_to_file(text, output_wav)
                self.engine.runAndWait()
                self.progress_bar.setValue(80)
            else:
                try:
                    tts = gTTS(text=text, lang=lang_code, slow=False)
                    self.progress_bar.setValue(40)
                    
                    tts.save(temp_mp3)
                    self.progress_bar.setValue(60)
                    
                    audio = AudioSegment.from_mp3(temp_mp3)
                    audio.export(output_wav, format="wav")
                    self.progress_bar.setValue(80)
                    
                    if os.path.exists(temp_mp3):
                        os.remove(temp_mp3)
                except Exception as e:
                    raise Exception(f"gTTS error: {str(e)}")
            
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
                extracted_text = self.extract_text_from_pdf(file_path)
                if extracted_text:
                    self.text_input.setText(extracted_text)
                    QMessageBox.information(self, "Success", "Text extracted successfully from the PDF.")
                else:
                    QMessageBox.warning(self, "PDF Error", "No text found in the PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_pdf(self, pdf_path):
        try:
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
        app.setStyle('Fusion') 
        window = TextToSpeechApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {str(e)}")

        
