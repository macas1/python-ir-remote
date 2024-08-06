from InfraredData import InfraredData
from MonitorState import MonitorState
from time import sleep
import serial, pyautogui, os, json

class InfraredMonitor: 
    ser: serial.Serial = None
    mapping: dict = None
    actions: dict = None
    persistant_state: MonitorState = None
    debug: bool = None

    def __init__(
        self, 
        serial_port, 
        serial_baudrate,
        input_to_name_map,
        debug = False,
        connection_attempts = 4,
        connection_sleep = 5
    ):
        self.mapping = input_to_name_map
        self.debug = debug
        self.ser = InfraredMonitor.get_serial_connection(
            serial_port, 
            serial_baudrate, 
            connection_attempts,
            connection_sleep
        )
        self.actions = InfraredMonitor.get_actions()
        pyautogui.FAILSAFE = False

    @staticmethod
    def get_serial_connection(serial_port, serial_baudrate, connection_attempts, connection_sleep):
        while connection_attempts != 0:
            try:
                return serial.Serial(
                    port=serial_port, 
                    baudrate=serial_baudrate, 
                    timeout=None
                )
            except Exception as e:
                message = str(e)
                connection_attempts -= 1
                print(message[:1].upper() + message[1:])
                if connection_attempts != 0:
                    print("Trying again in", connection_sleep, "seconds.", connection_attempts, "attempt(s) left.")
                    sleep(connection_sleep)

        raise serial.SerialException("Could not open port '" + serial_port + "'.")

    @staticmethod
    def get_actions():
        actions = {}
        # Get actions from jason file in a dict format for quick referencing
        with open('Actions.json', 'r') as json_file:
            for action_item in json.load(json_file):
                try:
                    trigger_value = action_item["TriggerValue"]
                except KeyError:
                    continue
                del action_item["TriggerValue"]
                if trigger_value not in actions:
                    actions[trigger_value] = []
                actions[trigger_value].append(action_item)
        
        attr_func_names = []
        for action_key in actions:
            action_item = actions[action_key]

            # Sort common actions by requirement count
            action_item.sort(key=lambda act: len(act["Requirements"]), reverse=True)

            # Collect class function names for validation
            for action in action_item:
                try:
                    for requirement in action["Requirements"]:
                        attr_func_names.append('requirement_' + requirement)
                    attr_func_names.append("press_" + action["PressType"])
                    attr_func_names.append("action_" + action["Action"])
                except KeyError:
                    raise KeyError("An item in your 'Actions.json' structure is missing a required key. See previous error for more details.")
                    

        # Validate requirement, press & action functions
        attr_func_names.sort()
        for func_name in attr_func_names:
            if not hasattr(InfraredMonitor, func_name):
                print("WARNING: InfraredMonitor method '" + func_name + "' does not exist.")

        #Return
        return actions
    
    def main_loop(self):
        print('Monitor ready.')
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

            # Run action
            self.dubug_print("\n" + str(vars(data)) + ", HoldDuration: " + str(self.persistant_state.held_duration))
            self.run_action(data.value)

    def run_action(self, value: str):
        if value in self.actions:
            for action in self.actions[value]:
                # Check if all requirements are met
                requirement_met = True
                for requirement in action["Requirements"]:
                    if not getattr(self, 'requirement_' + requirement)():
                        requirement_met = False
                        break
                # If requirements are met, try to use this action and ignore all others
                if requirement_met:
                    # Run the action if if should run on this press/hold tick
                    press_function_result = getattr(self, 'press_' + action["PressType"])()
                    self.dubug_print(str(action) + ", Pressed: " + str(press_function_result))
                    if press_function_result: 
                        getattr(self, 'action_' + action["Action"])()
                    break
    
    def dubug_print(self, string: str):
        if self.debug:
            print(string)

    def action_press_volume_up(self):
        pyautogui.press('volumeup')
    
    def action_press_volume_down(self):
        pyautogui.press('volumedown')

    def action_press_volume_mute(self):
        pyautogui.press('volumemute')

    def action_press_pause(self):
        pyautogui.press('pause')

    def action_press_playpause(self):
        pyautogui.press('playpause')

    def action_press_f(self):
        pyautogui.press('f')

    def action_press_c(self):
        pyautogui.press('c')

    def action_press_nexttrack(self):
        pyautogui.press('nexttrack')

    def action_press_l(self):
        pyautogui.press('l')

    def action_press_prevtrack(self):
        pyautogui.press('prevtrack')

    def action_press_j(self):
        pyautogui.press('j')
        
    def action_press_shift_n(self):
        with pyautogui.hold('shift'):
            pyautogui.press('n')

    def action_press_shift_p(self):
        with pyautogui.hold('shift'):
            pyautogui.press('p')   

    def action_test(self):
        print(pyautogui.getActiveWindow())

    def action_begin_shutdown(self):
        os.system('shutdown -s -t 5')
        self.persistant_state.shutdown_started = True

    def action_cancel_shutdown(self):
        os.system('shutdown -a')
        self.persistant_state.shutdown_started = False

    def requirement_shutting_down(self):
        return self.persistant_state.shutdown_started == True

    def requirement_youtube_focussed(self):
        return ' - YouTube' in pyautogui.getActiveWindowTitle() # This has only been tested for Edge

    def press_all(self):
        return True

    def press_initial(self):
        return self.persistant_state.held_duration == 0

    def press_slow_hold(self):
        return self.persistant_state.held_duration % 2 == 0