from MapLoader import MapLoader
from InfraredMonitor import InfraredMonitor

# Settings
mapping_files: list[str] = ['TVAKB73715603']
auduino_port: str = 'COM4'
auduino_baudrate: int = 9600

# Main
if __name__ == '__main__':
    mapping = MapLoader.load_map(mapping_files)
    monitor = InfraredMonitor(
        auduino_port, 
        auduino_baudrate,
        mapping,
        debug=True
    )
    monitor.main_loop()