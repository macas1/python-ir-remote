from MapLoader import MapLoader
from InfraredMonitor import InfraredMonitor

# Settings
mapping_files = ["TVAKB73715603"]
auduino_port = 'COM4'
auduino_baudrate = 9600

# Main
if __name__ == "__main__":
    mapping = MapLoader.load_map(mapping_files)
    monitor = InfraredMonitor(
        auduino_port, 
        auduino_baudrate,
        mapping
    )
    monitor.main_loop()