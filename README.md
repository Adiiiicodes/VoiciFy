# Voicify - Text-to-Speech Application

## **Overview**
Voicify is an intuitive desktop application that converts text into speech, supporting multiple languages and customizable voice settings. With features like PDF text extraction, adjustable speech rates, and playback/download options, it is designed for diverse use cases, including accessibility, language learning, and efficient multitasking.

---

## **Features**

### 1. **Multi-Language Support**
   - Convert text to speech in popular languages such as:
     - English
     - Spanish
     - French
     - German
     - Italian
     - Portuguese
     - Russian
     - Japanese
     - Korean
     - Chinese (Simplified)
   - Powered by **Google Text-to-Speech (gTTS)** for non-English languages.

### 2. **Customizable Voice Selection (English Only)**
   - Choose between **Male** and **Female** voice options using the pyttsx3 library.
   - Adjustable voice speed for optimal listening experience.

### 3. **PDF Text-to-Speech Conversion**
   - Upload any PDF document and extract text seamlessly for conversion into speech.

### 4. **Adjustable Speech Rate**
   - Control the speed of speech output via an intuitive slider.

### 5. **Playback & Download Options**
   - Play the generated speech directly within the app.
   - Save the speech audio as a downloadable file in `.wav` format.

### 6. **User-Friendly Interface**
   - Modern design with styled widgets, frames, and clear labels.
   - Easy navigation for users of all technical levels.

---

## **Tech Stack**

### **Programming Language**
- **Python 3.9+**
  - A powerful, high-level programming language used for application development.

### **GUI Framework**
- **PyQt5**
  - Provides a modern and responsive graphical user interface.
  - Features like sliders, dropdowns, buttons, and frames are implemented using PyQt5 widgets.

### **Text-to-Speech Engines**
- **pyttsx3**
  - Text-to-speech conversion engine for offline speech synthesis.
  - Supports voice customization and adjustable speech rate.
- **gTTS (Google Text-to-Speech)**
  - Converts text to speech for non-English languages.

### **Audio Processing**
- **pydub**
  - Used for audio manipulation (e.g., converting audio formats from MP3 to WAV).
- **winsound**
  - Native playback of WAV audio files on Windows.

### **PDF Processing**
- **PyPDF2**
  - Reads text from PDF documents for text extraction.

### **Image & OCR**
- **Pillow (PIL)** and **pytesseract**
  - Prepares image-based PDFs for text extraction via Optical Character Recognition (OCR).

### **Other Libraries**
- **tempfile**
  - Manages temporary directories for audio processing.
- **os, sys, shutil**
  - File handling and system operations.
- **io**
  - Provides stream handling for reading/writing in memory.

---

## **Installation**

### **System Requirements**
- Windows OS
- Python 3.9 or higher
- At least 2GB RAM

### **Dependencies**
The following libraries are required to run Voicify:
- `pyttsx3`
- `gTTS`
- `PyQt5`
- `pydub`
- `PyPDF2`
- `pytesseract`
- `Pillow`

To install all dependencies in one go, run:
```bash
pip install pyttsx3 gTTS PyQt5 pydub PyPDF2 pytesseract Pillow
```

### **Tesseract OCR Installation (Optional for PDFs with Images)**
1. Download and install Tesseract OCR from [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract).
2. Add Tesseract to your system PATH.

---

## **Usage Instructions**

1. **Launch the Application**
   - Run the `TextToSpeechApp` script:
     ```bash
     python <filename>.py
     ```

2. **Select Language**
   - Use the dropdown menu to choose the language for text-to-speech conversion.

3. **Enter or Upload Text**
   - Directly type text into the input box or upload a PDF file for text extraction.

4. **Choose Voice & Adjust Speed (English Only)**
   - Select between male or female voice and adjust the speed using the slider.

5. **Convert Text to Speech**
   - Click the "Convert" button to generate the speech audio.

6. **Playback & Download**
   - Use the "Play" button to listen to the audio or "Download" to save it locally.

---

## **File Structure**
```
Voicify/
├── main.py                # Main application script
├── requirements.txt       # Dependency list
├── README.md              # Project documentation
└── assets/                # Icons, logos, or additional files (if any)
```

---

## **Future Enhancements**
- **Support for Additional File Formats**  
   Extend file input support to formats like DOCX and TXT.  

- **Cloud-Based Storage**  
   Enable cloud integration for saving and accessing audio files.  

- **Enhanced Voice Options**  
   Add regional accent support for English (e.g., Indian, British, American).

---

## **Acknowledgments**
- Thanks to open-source libraries and tools like **PyQt5**, **pyttsx3**, and **gTTS** for making this project possible.
- Inspired by the need for accessible and customizable text-to-speech solutions.

---

## **License**
This project is licensed under the MIT License. See the LICENSE file for more details.

--- 

Feel free to reach out for contributions, feedback, or collaborations! 😊
