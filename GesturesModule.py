import cv2
import numpy as np
import pyautogui

from MouseModule import FullWindowsGestureControl


class GesturesModule(FullWindowsGestureControl):
    def __init__(self, sensitivity=1.5, scroll_speed=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sensitivity = sensitivity
        self.scroll_speed = scroll_speed
        self.running = False

    def handle_movement_gestures(self, fingers, img):
        if fingers[1] == 1 and fingers[2:] == [0, 0, 0, 0]:  # Moving Mode
            x1, y1 = self.lm_list[8][1:]
            x2 = np.interp(
                x1, (self.frame_r, self.width - self.frame_r), (0, pyautogui.size()[0])
            )
            y2 = np.interp(
                y1, (self.frame_r, self.height - self.frame_r), (0, pyautogui.size()[1])
            )
            self.clocX = (
                self.plocX + (x2 - self.plocX) / self.smoothening * self.sensitivity
            )
            self.clocY = (
                self.plocY + (y2 - self.plocY) / self.smoothening * self.sensitivity
            )
            pyautogui.moveTo(self.clocX, self.clocY)
            self.plocX, self.plocY = self.clocX, self.clocY

    def handle_scroll_gestures(self, fingers):
        if fingers == [0, 1, 1, 1, 1]:  # Scroll Mode
            for i in range(1, 5):
                if self.lm_list[4 * i][2] < self.height - self.frame_r:
                    pyautogui.scroll(self.scroll_speed)
                elif self.lm_list[4 * i][2] > self.frame_r:
                    pyautogui.scroll(-self.scroll_speed)

                # Scroll up if the fingertip is above the frame threshold
                if self.lm_list[4 * i + 1][2] < self.height - self.frame_r:
                    pyautogui.scroll(self.scroll_speed)
                # Scroll down if the fingertip is below the frame threshold
                elif self.lm_list[4 * i + 1][2] > self.frame_r:
                    pyautogui.scroll(-self.scroll_speed)

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        cap.set(3, self.width)
        cap.set(4, self.height)
        while self.running and cap.isOpened():
            success, img = cap.read()
            if not success:
                break
            img = cv2.flip(img, 1)  # Flip the image if needed
            img = self.find_hands(img)
            self.lm_list = self.find_position(img)
            if len(self.lm_list) != 0:
                # Proceed with the rest of your gesture recognition logic here
                pass
            # You must call cv2.imshow to display the image frame
            cv2.imshow("Gesture Control", img)
            # Add a waitKey call to give the window a chance to update,
            # and check if the user has pressed the 'q' key to break the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        while cap.isOpened():
            success, img = cap.read()
            if not success:
                break
            img = cv2.flip(img, 1)
            img = self.find_hands(img)
            self.lm_list = self.find_position(img, draw=True)
            if self.lm_list:
                fingers = self.fingers_up()
                # Mouse Movement Gestures
                self.handle_movement_gestures(fingers, img)
                # Scroll Gestures
                self.handle_scroll_gestures(fingers)

            self.show_instructions(img)
            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create an instance of the gesture control class
    gesture_control = FullWindowsGestureControl()
    # Call the 'run' method to start the gesture control
    gesture_control.run()
