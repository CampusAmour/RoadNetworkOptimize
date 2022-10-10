import os
from utils.ui import TrafficLoadWindow
from PyQt5.QtWidgets import QApplication

class TrafficSystem():
    def __init__(self):
        self.base_path = os.getcwd()
        self.app = QApplication([])
        self.system_window = TrafficLoadWindow(self.base_path)

    def run(self):
        self.system_window.ui.show()
        self.app.exec_()


if __name__ == "__main__":
    # app = QApplication([])
    # window = TrafficLoadWindow("./utils/traffic_load_window.ui")
    # window.ui.show()
    # app.exec_()

    system = TrafficSystem()
    system.run()
