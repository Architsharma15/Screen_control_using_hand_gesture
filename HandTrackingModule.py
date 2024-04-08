import cv2
import mediapipe as mp
import time


class HandTrackingModule:
    def __init__(self, mode=False, max_hands=2, complexity=1, detection_confidence=0.5, tracking_confidence=0.5):
        self.mode = mode
        self.maxHands = max_hands
        self.complexity = complexity
        self.detectionConfidence = detection_confidence
        self.trackingConfidence = tracking_confidence
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity, self.detectionConfidence,
                                        self.trackingConfidence)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_landmarks,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        self.lm_list = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(hand.landmark):
                height, width, _ = img.shape
                cx, cy = int(lm.x * width), int(lm.y * height)
                self.lm_list.append((id, cx, cy))
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return self.lm_list

    def fingers_up(self):
        fingers = []
        if self.lm_list:
            # Thumb
            if self.lm_list[self.tipIds[0]][1] > self.lm_list[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # Fingers
            for id in range(1, 5):
                if self.lm_list[self.tipIds[id]][2] < self.lm_list[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def get_handedness(self):
        handedness_list = []
        if self.results.multi_handedness:
            for hand_handedness in self.results.multi_handedness:
                handedness = hand_handedness.classification[0].label
                handedness_list.append(handedness)
        return handedness_list


    def draw_on_finger(self, img, finger_id, color=(0, 255, 0), radius=10, thickness=-1):
        if self.lm_list:
            x, y = self.lm_list[finger_id][1], self.lm_list[finger_id][2]
            cv2.circle(img, (x, y), radius, color, thickness)


def main():
    cap = cv2.VideoCapture(1)
    prev_time = 0
    detector = HandTrackingModule()

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        landmark_list = detector.find_position(img)
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        fingers = detector.fingers_up()
        if fingers:
            if fingers[1]:  # If the index finger is raised
                detector.draw_on_finger(img, 8, color=(0, 255, 0))  # Draw green circle
            else:
                detector.draw_on_finger(img, 8, color=(0, 0, 255))  # Draw red circle
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()