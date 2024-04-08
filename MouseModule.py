import cv2
import time
import numpy as np
import pyautogui
import math
from HandTrackingModule import HandTrackingModule


class FullWindowsGestureControl(HandTrackingModule):
    def __init__(
            self,
            width=640,
            height=480,
            frame_r=100,
            smoothening=5,
            sensitivity=1.5,
            scroll_speed=20,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.frame_r = frame_r
        self.smoothening = smoothening
        self.sensitivity = sensitivity
        self.scroll_speed = scroll_speed
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.pinch_threshold = 40


    def find_distance(self, p1, p2, img, draw=True):
        # Get the landmarks of the points
        x1, y1 = self.lm_list[p1][1:3]
        x2, y2 = self.lm_list[p2][1:3]
        # Calculate the distance
        distance = math.hypot(x2 - x1, y2 - y1)
        if draw:
            # Draw line and circle for the points
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (x1, y1), 5, (255, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 5, (255, 255, 0), cv2.FILLED)
        return distance

    def show_instructions(self, img):
        instructions = [
            "Index Up: Move Mouse",
            "Index + Thumb Touch: Left Click",
            "Middle + Thumb Touch: Right Click",
            "Index + Middle Up: Scroll",
            "Thumb + Index Pinch: Zoom",
            "Thumb Up + Pinky Up: Drag [Placeholder]",  # Example additional instruction
        ]
        y = 10
        for instruction in instructions:
            cv2.putText(
                img, instruction, (10, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1
            )
            y += 15

    def is_inside_gesture_box(self, x, y):
        # Define the gesture box coordinates (top left corner and bottom right corner)
        gesture_box_top_left = (self.frame_r, self.frame_r)
        gesture_box_bottom_right = (self.width - self.frame_r, self.height - self.frame_r)

        # Check if the point (x, y) is inside the gesture box
        if (gesture_box_top_left[0] <= x <= gesture_box_bottom_right[0] and
                gesture_box_top_left[1] <= y <= gesture_box_bottom_right[1]):
            return True
        else:
            return False

    def draw_on_finger(self, img, finger_id, color=(0, 255, 0), radius=10, thickness=-1):
        if len(self.lm_list) > finger_id:
            x, y = self.lm_list[finger_id][1], self.lm_list[finger_id][2]
            cv2.circle(img, (x, y), radius, color, thickness)

    def run(self):
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # reduce width
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # reduce height
        cap.set(3, self.width)
        cap.set(4, self.height)


        while cap.isOpened():
            success, img = cap.read()
            if not success:
                break
            img = cv2.flip(img, 1)
            img = self.find_hands(img)
            lm_list = self.find_position(img, draw=False)
            self.lm_list = lm_list

            if lm_list:
                fingers = self.fingers_up()

                # Debug: Print the state of the fingers
                print(f"Fingers State: {fingers}")
                # ... moving mode code

                # Drawing the gesture box for visual reference
                cv2.rectangle(img, (self.frame_r, self.frame_r), (self.width - self.frame_r, self.height - self.frame_r), (255, 0, 255), 2)
                fingers = self.fingers_up()
                if fingers[1]:  # If the index finger is raised
                    self.draw_on_finger(img, 8, color=(0, 255, 0))  # Draw green circle
                else:
                    self.draw_on_finger(img, 8, color=(0, 0, 255))
                    # Moving Mode: Index finger is up, other fingers are down.
                # Moving Mode: Index finger is up, other fingers are down.
                if fingers == [0, 1, 0, 0, 0]:
                    # Get the tip of the index finger
                    x1, y1 = lm_list[8][1], lm_list[8][2]

                    # Convert coordinates to the screen size
                    x2 = np.interp(x1, (self.frame_r, self.width - self.frame_r), (0, pyautogui.size()[0]))
                    y2 = np.interp(y1, (self.frame_r, self.height - self.frame_r), (0, pyautogui.size()[1]))

                    # Smoothen Values
                    self.clocX = self.plocX + (x2 - self.plocX) / self.smoothening
                    self.clocY = self.plocY + (y2 - self.plocY) / self.smoothening
                    # Move the mouse
                    pyautogui.moveTo(self.clocX, self.clocY)

                    # Update the previous location
                    self.plocX, self.plocY = self.clocX, self.clocY
                # Gesture for Left Click: Thumb and index finger are close.
                if fingers[1] == 1 and fingers[0] == 1 and fingers[2:] == [0, 0, 0]:
                    distance = self.find_distance(8, 4, img, draw=False)
                    if distance < self.pinch_threshold:
                        pyautogui.click()
                # Gesture for Right Click: Thumb and middle finger are close.
                if fingers[1] == 0 and fingers[0] == 1 and fingers[2] == 1:
                    distance = self.find_distance(12, 4, img, draw=False)
                    if distance < self.pinch_threshold:
                        pyautogui.click(button="right")

                # Scroll Gestures: Index and middle finger are up for scrolling up, down otherwise.
                if fingers[1] == 1 and fingers[2] == 1:
                    for i in range(1, 5):
                        if lm_list[4 * i][2] < self.height - self.frame_r:
                            pyautogui.scroll(self.scroll_speed)
                        elif lm_list[4 * i][2] > self.frame_r:
                            pyautogui.scroll(-self.scroll_speed)

                # Zoom Gesture: Thumb and index finger pinch.
                if (
                        fingers[0] == 1
                        and fingers[1] == 1
                        and all(f == 0 for f in fingers[2:])
                ):
                    distance_zoom = self.find_distance(4, 8, img, draw=False)

                    if distance_zoom < self.pinch_threshold:
                        pyautogui.keyDown("ctrl")
                        pyautogui.scroll(100)
                        pyautogui.keyUp("ctrl")
                    elif distance_zoom > self.pinch_threshold:
                        pyautogui.keyDown("ctrl")
                        pyautogui.scroll(-100)
                        pyautogui.keyUp("ctrl")

                # Placeholder for the start of the drag gesture (adjust this to your needs)
                if fingers[0] == 1 and fingers[4] == 1:
                    # Logic to initiate mouse drag...
                    pass  # Replace with actual drag implementation

            # Display instructions for available gestures
            self.show_instructions(img)
            cv2.rectangle(img, (self.frame_r, self.frame_r), (self.width - self.frame_r, self.height - self.frame_r),
                          (255, 0, 255), 2)
            cv2.imshow("Image", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False  # Set the running flag to False

    def update(self):
        # Call this method in a loop to check if running is still True
        if not self.running:
            # if running is False, release resources and close windows
            cv2.destroyAllWindows()
            return False  # Indicate that we've stopped
        # ... (rest of the code that should run while the system is active)
        return True  # Indicate that we're still running


if __name__ == "__main__":
    # Create an instance of the gesture control class
    gesture_control = FullWindowsGestureControl()
    # Call the 'run' method to start the gesture control
    gesture_control.run()
