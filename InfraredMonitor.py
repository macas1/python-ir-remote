from InfraredData import InfraredData
import serial, pyautogui, os

class InfraredMonitor: 
    ser = None
    mapping = None

    def __init__(
        self, 
        serial_port, 
        serial_baudrate,
        input_to_name_map
    ):
        # Init serial connection and required data
        self.ser = serial.Serial(
            port=serial_port, 
            baudrate=serial_baudrate, 
            timeout=None
        )
        self.mapping = input_to_name_map
    
    def main_loop(self):
        previous_value = None
        while True:
            data = InfraredData()

            # Wait for next raw input and store it
            data.raw_value = self.ser.readline().strip().decode("utf-8") 
            
            # Get mapped value from raw input
            if data.raw_value in self.mapping: 
                data.value = self.mapping[data.raw_value]
            else:
                data.value = "UNKNOWN"

            # Handle special hold characters
            if data.value == "SPECIAL HELD":
                data.value = previous_value
                data.is_held = True
            else:
                data.is_held = False

            # Action
            InfraredMonitor.run_action(data)

            # Prepare for next raw input
            previous_value = data.value

    @staticmethod
    def run_action(data: InfraredData):
        print(vars(data))
        if data.value == "VOLUME UP": pyautogui.press("volumeup")
        if data.value == "VOLUME DOWN": pyautogui.press("volumedown")
        if data.value == "MUTE" and not data.is_held: pyautogui.press("volumemute")
        if data.value == "PAUSE" and not data.is_held: pyautogui.press("pause")
        if data.value == "PLAY" and not data.is_held: pyautogui.press("playpause")
        if data.value == "FASTFORWARD" and not data.is_held: pyautogui.press("nexttrack")
        if data.value == "REWIND" and not data.is_held: pyautogui.press("prevtrack")
        if data.value == "ON/OFF" and not data.is_held: os.system('shutdown -s -t 5')
        if data.value == "TV/RAD" and not data.is_held: os.system('shutdown -a')
        if data.value == "1": print(pyautogui.getActiveWindow())


        