# This is just a simple example to illustrate the main application script structure.
from HandTrackingModule import HandTrackingModule
from GesturesModule import GesturesModule
from MouseModule import FullWindowsGestureControl
from SomeUIFramework import show_gui  # This is a placeholder for a UI framework you might use.


def main():
    # Initialize the gesture control system.
    gesture_control = FullWindowsGestureControl()

    # You could have a UI function that triggers this run method when the user wants to start gesture control.
    show_gui(gesture_control)


if __name__ == "__main__":
    main()