# import necessary modules
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
# Import the gesture module here
from GesturesModule import GesturesModule

class GUIApp(QMainWindow):

  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    # Main window settings
    self.setWindowTitle('Gesture Control Software')
    self.setGeometry(100, 100, 280, 170)
    # Start button
    self.startButton = QPushButton('Start Gesture Control', self)
    self.startButton.clicked.connect(self.startGestureControl)
    # Stop button
    self.stopButton = QPushButton('Stop Gesture Control', self)
    self.stopButton.clicked.connect(self.stopGestureControl)
    # Status label
    self.statusLabel = QLabel('Status: Ready', self)
    # Layout settings
    layout = QVBoxLayout()
    layout.addWidget(self.startButton)
    layout.addWidget(self.stopButton)
    layout.addWidget(self.statusLabel)
    # Central Widget
    centralWidget = QWidget()
    centralWidget.setLayout(layout)
    self.setCentralWidget(centralWidget)

  def startGestureControl(self):
    self.statusLabel.setText('Status: Running')
    # Placeholder for starting gesture control logic
    # gesture_control.run()
  def stopGestureControl(self):
    self.statusLabel.setText('Status: Stopped')
    # Placeholder for stopping gesture control logic
    # gesture_control.stop()

def main():
  # Make sure we have a QApplication instance
  app = QApplication(
    sys.argv) if QApplication.instance() is None else QApplication.instance()
  # Create a GUI application instance
  gui_app = GUIApp()
  gui_app.show()
  # Initialize the gesture control system from GesturesModule
  gesture_control = GesturesModule()  # Instantiate GesturesModule
  # Connect the GUI button to the gesture control run and stop methods
  gui_app.startButton.clicked.connect(gesture_control.run)
  gui_app.stopButton.clicked.connect(gesture_control.stop)
  # Exit cleanly when the application is closed
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()