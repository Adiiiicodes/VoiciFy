import os
import tempfile
from gtts import gTTS
from playsound import playsound
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QComboBox
from PyQt5.QtCore import Qt

class TextToSpeechApp(QWidget):
    def __init__(self):
        super().__init__()

        # Supported languages for gTTS
        self.supported_languages = {
            "Afrikaans": "af", "Arabic": "ar", "Bulgarian": "bg", "Catalan": "ca", "Chinese": "zh-cn",
            "Croatian": "hr", "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en", "Finnish": "fi",
            "French": "fr", "German": "de", "Greek": "el", "Hindi": "hi", "Hungarian": "hu", "Icelandic": "is",
            "Indonesian": "id", "Italian": "it", "Japanese": "ja", "Korean": "ko", "Norwegian": "no",
            "Polish": "pl", "Portuguese": "pt", "Romanian": "ro", "Russian": "ru", "Slovak": "sk",
            "Spanish": "es", "Swahili": "sw", "Swedish": "sv", "Tamil": "ta", "Thai": "th", "Turkish": "tr",
            "Ukrainian": "uk", "Vietnamese": "vi", "Welsh": "cy"
        }

        # Set up the GUI layout
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Language selection dropdown
        self.language_label = QLabel("Select Language:")
        layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox(self)
        for language in self.supported_languages.keys():
            self.language_dropdown.addItem(language)
        layout.addWidget(self.language_dropdown)

        # Text input
        self.text_label = QLabel("Enter Text:")
        layout.addWidget(self.text_label)
        
        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        # Speech rate slider
        self.rate_label = QLabel("Select Speech Rate (not supported in gTTS):")
        layout.addWidget(self.rate_label)

        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setMinimum(100)
        self.rate_slider.setMaximum(200)
        self.rate_slider.setValue(150)  # Default speech rate
        layout.addWidget(self.rate_slider)

        # Convert button
        self.convert_button = QPushButton("Convert to Speech")
        self.convert_button.clicked.connect(self.text_to_speech)
        layout.addWidget(self.convert_button)

        # Set layout and window properties
        self.setLayout(layout)
        self.setWindowTitle("VoxiFy - Text to Speech Converter")
        self.setGeometry(300, 300, 300, 250)

    def text_to_speech(self):
        # Get the selected language's language code
        language = self.language_dropdown.currentText()
        language_code = self.supported_languages[language]
        
        # Get the input text
        text = self.text_input.text()

        # Generate speech using gTTS
        tts = gTTS(text=text, lang=language_code, slow=False)

        # Use a full path for the temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            tts.save(temp_audio_path)

        # Play the audio
        try:
            playsound(temp_audio_path)
        finally:
            # Clean up the temporary file
            os.remove(temp_audio_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tts_app = TextToSpeechApp()
    tts_app.show()
    sys.exit(app.exec_())
