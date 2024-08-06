class MonitorState:
    shutdown_started: bool
    held_duration: int
    previous_value: str | None = None
    previous_value_time: int | None = None

    def __init__(self):
        self.shutdown_started = False
        self.held_duration = 0