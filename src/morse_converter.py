import time

class MorseConverter:
    """
    Handles Morse code conversion logic with improved timing
    """
    def __init__(self):
        # Morse code dictionary (expanded)
        self.morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
            '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
            '-----': '0', '--..--': ',', '.-.-.-': '.', '..--..': '?', 
            '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&',
            '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+',
            '-....-': '-', '..--.-': '_', '.-..-.': '"', '...-..-': '$',
            '.--.-.': '@'
        }
        
        # Timing thresholds (seconds) - adjusted for better usability
        self.DOT_MAX = 1       # Maximum duration for dot (short blink)
        self.DASH_MIN = 2      # Minimum duration for dash (long blink)
        self.DASH_MAX = 3      # Maximum blink duration
        self.CHAR_PAUSE = 3    # Time to complete character
        self.WORD_PAUSE = 4    # Time to complete word
        
        # State tracking
        self.current_code = ""
        self.decoded_text = ""
        self.last_char_time = time.time()
    
    def add_signal(self, signal):
        """
        Add a dot or dash signal to current Morse code sequence
        """
        if signal in [".", "-"]:
            self.current_code += signal
    
    def process_timing(self, current_time, last_blink_end):
        """
        Process timing logic to determine if character or word is complete
        """
        # Check for character completion
        time_since_blink = current_time - last_blink_end
        
        if self.current_code and time_since_blink >= self.CHAR_PAUSE:
            char = self.morse_dict.get(self.current_code, "#")
            self.decoded_text += char
            print(f"Decoded: {char} from {self.current_code}")
            
            self.current_code = ""
            self.last_char_time = current_time
        
        # Check for word completion
        time_since_char = current_time - self.last_char_time
        if time_since_char >= self.WORD_PAUSE and self.decoded_text and self.decoded_text[-1] != " ":
            self.decoded_text += " "
            print("Space added")
    
    def get_morse_table(self):
        """
        Create a 2D array for the Morse code table display
        """
        morse_items = sorted(self.morse_dict.items(), key=lambda x: x[1])
        
        # Create pairs for two columns
        result = []
        for i in range(0, len(morse_items), 2):
            row = []
            if i < len(morse_items):
                row.append((morse_items[i][1], morse_items[i][0]))
            if i+1 < len(morse_items):
                row.append((morse_items[i+1][1], morse_items[i+1][0]))
            if row:
                result.append(row)
        return result