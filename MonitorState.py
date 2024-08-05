class MonitorState:
    shutdown_started: bool = None
    held_duration: int = None
    previous_value: str | None = None

    def __init__(self):
        self.shutdown_started = False
        self.held_duration = 0