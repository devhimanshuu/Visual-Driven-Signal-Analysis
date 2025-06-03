# Morse Code Eye Blink Converter

This system converts eye blinks to Morse code with a local web interface.

## Features

- Real-time eye blink detection using OpenCV
- Conversion of blinks to Morse code (short blinks for dots, long blinks for dashes)
- Text-to-speech feedback for decoded characters
- Web interface with split view:
  - Left side: Live camera feed with blink detection
  - Right side: Morse code reference and decoded text

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:8081`

## How to Use

- Position yourself in front of the camera
- Blink to input Morse code:
  - Short blink (< 1s) = Dot (.)
  - Long blink (2-2.5s) = Dash (-)
  - Pause for 10s to complete a character
  - Pause for 3s after a character to add a space

## Project Structure

- `app.py`: Main application entry point
- `src/`: Core functionality modules
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files