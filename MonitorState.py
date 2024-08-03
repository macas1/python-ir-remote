class MonitorState:
    shutdown_started = None
    previous_value = None
    held_duration = None

    def __init__(self):
        self.shutdown_started = False
        self.held_duration = 0