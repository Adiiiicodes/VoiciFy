import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QComboBox
from PyQt5.QtCore import Qt
import pyttsx3

class TextToSpeechApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        
        # Set up the GUI layout
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Language selection dropdown
        self.language_label = QLabel("Select Language:")
        layout.addWidget(self.language_label)

        self.language_dropdown = QComboBox(self)
        for i, voice in enumerate(self.voices):
            # Get the language or set a default if unavailable
            language = voice.languages[0] if voice.languages else "Unknown Language"
            self.language_dropdown.addItem(f"{voice.name} ({language})", i)
        layout.addWidget(self.language_dropdown)

        # Text input
        self.text_label = QLabel("Enter Text:")
        layout.addWidget(self.text_label)
        
        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        # Speech rate slider
        self.rate_label = QLabel("Select Speech Rate:")
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
        # Get the selected language's voice ID
        voice_id = self.language_dropdown.currentData()
        
        # Get the input text
        text = self.text_input.text()
        
        # Get the selected speech rate
        speech_rate = self.rate_slider.value()

        # Set voice and rate properties in the engine
        self.engine.setProperty('voice', self.voices[voice_id].id)
        self.engine.setProperty('rate', speech_rate)

        # Speak the text
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tts_app = TextToSpeechApp()
    tts_app.show()
    sys.exit(app.exec_())
