from InfraredData import InfraredData
from MonitorState import MonitorState
import serial, pyautogui, os

class InfraredMonitor: 
    ser = None
    mapping = None
    actions = None
    persistant_state = None

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
        self.actions = {
            'ON/OFF': self.action_on_off,
            'RATIO': self.action_ratio,
            'TEXT': self.action_text,
            'VOLUME UP': self.action_volume_up,
            'VOLUME DOWN': self.action_volume_down,
            'PAGE UP': self.action_page_up,
            'PAGE DOWN': self.action_page_down,
            'MUTE': self.action_mute,
            'PAUSE': self.action_pause, 
            'PLAY': self.action_play, 
            'FASTFORWARD': self.action_fastforward, 
            'REWIND': self.action_rewind, 
            'RED': self.action_red,
        }
    
    def main_loop(self):
        print('Monitor ready')
        self.persistant_state = MonitorState()
        while True:
            data = InfraredData()

            # Wait for next raw input and store it
            data.raw_value = self.ser.readline().strip().decode('utf-8') 
            
            # Get mapped value from raw input
            if data.raw_value in self.mapping: 
                data.value = self.mapping[data.raw_value]
            else:
                data.value = 'UNKNOWN'

            # Handle special hold characters
            if data.value == 'SPECIAL HELD':
                data.value = self.persistant_state.previous_value
                self.persistant_state.held_duration += 1
            else:
                self.persistant_state.previous_value = data.value
                self.persistant_state.held_duration = 0

            # Run action (TODO: Maybe have a try statement here just in case)
            print(str(vars(data)) + " - " + str(self.persistant_state.held_duration))
            if data.value in self.actions:
                self.actions[data.value](data)

    def action_volume_up(self, data: InfraredData):
        pyautogui.press('volumeup')
    
    def action_volume_down(self, data: InfraredData):
        pyautogui.press('volumedown')

    def action_mute(self, data: InfraredData):
        if not self.state_is_held():
            pyautogui.press('volumemute')

    def action_pause(self, data: InfraredData):
        if not self.state_is_held():
            pyautogui.press('pause')

    def action_play(self, data: InfraredData):
        if not self.state_is_held():
            pyautogui.press('playpause')

    def action_ratio(self, data: InfraredData):
        if not self.state_is_held() and self.state_youtube_is_focussed(pyautogui.getActiveWindowTitle()):
            pyautogui.press('f')

    def action_text(self, data: InfraredData):
        if not self.state_is_held() and self.state_youtube_is_focussed(pyautogui.getActiveWindowTitle()):
            pyautogui.press('c')

    def action_fastforward(self, data: InfraredData):
        if self.state_is_held_tick(2) and self.state_youtube_is_focussed(pyautogui.getActiveWindowTitle()):
            pyautogui.press('l')
        else:
            pyautogui.press('nexttrack')

    def action_rewind(self, data: InfraredData):
        if self.state_is_held_tick(2) and self.state_youtube_is_focussed(pyautogui.getActiveWindowTitle()):
            pyautogui.press('j')
        else:
            pyautogui.press('prevtrack')
        
    def action_page_up(self, data: InfraredData):
        if not self.state_is_held() and self.state_youtube_is_focussed(pyautogui.getActiveWindowTitle()):
            with pyautogui.hold('shift'):
                pyautogui.press('n')

    def action_page_down(self, data: InfraredData):
        if not self.state_is_held() and self.state_youtube_is_focussed(pyautogui.getActiveWindowTitle()):
            with pyautogui.hold('shift'):
                pyautogui.press('p')

    def action_on_off(self, data: InfraredData):
        if not self.state_is_held():
            if self.persistant_state.shutdown_started:
                os.system('shutdown -a')
                self.persistant_state.shutdown_started = False
            else:
                os.system('shutdown -s -t 10')
                self.persistant_state.shutdown_started = True

    def action_red(self, data: InfraredData):
        print(pyautogui.getActiveWindow())

    def state_youtube_is_focussed(self, active_window_title):
        return ' - YouTube' in active_window_title # This has only been tested for Edge
    
    def state_is_held(self):
        return self.persistant_state.held_duration > 0
    
    def state_is_held_tick(self, tick_rate):
        return self.persistant_state.held_duration % tick_rate == 0
