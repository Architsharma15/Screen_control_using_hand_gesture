import cv2
import mediapipe as mp
from HandTrackingModule import HandTrackingModule
import os
import numpy as np

# Depending on the system you might need to install one of these packages:
# For Windows: 'pycaw'
# For Linux: 'alsaaudio' or 'pulsectl'
# For MacOS: 'pyobjc-framework-Quartz' and 'pyobjc-core'
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Use screen-brightness-control for controlling brightness, which might need installation:
# pip install screen-brightness-control
import screen_brightness_control as sbc


class VolumeBrightnessGestureControl(HandTrackingModule):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Volume Control Initialization
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    self.volume = cast(interface, POINTER(IAudioEndpointVolume))
    self.vol_range = self.volume.GetVolumeRange()
    self.min_vol = self.vol_range[0]
    self.max_vol = self.vol_range[1]

  def run(self):
    cap = cv2.VideoCapture(1)
    initial_volume_distance = None
    initial_brightness_distance = None
    while True:
      success, img = cap.read()
      if not success:
        continue
      img = self.find_hands(img)
      self.lm_list = self.find_position(img, draw=False)
      if self.results.multi_hand_landmarks:
        handedness_list = self.get_handedness(
        )  # Retrieve handedness information
        # Now iterate using the handedness list
        for hand_no, hand in enumerate(self.results.multi_hand_landmarks):
          # Ensure handedness info is available for the current hand
          if hand_no < len(handedness_list):
            handedness = handedness_list[
                hand_no]  # Get handedness for current hand
          else:
            continue
          # Get landmark list for the specific hand
          self.lm_list = self.find_position(img, hand_no=hand_no, draw=False)
          # Get landmark list for the specific hand
          self.lm_list = self.find_position(img, hand_no=hand_no, draw=False)
          # For left hand - volume control
          if handedness == "Left":
            thumb_tip = self.lm_list[4][1:]
            index_tip = self.lm_list[8][1:]
            distance = int(
                np.hypot(index_tip[0] - thumb_tip[0],
                         index_tip[1] - thumb_tip[1]))

            print(f"Volume control distance: {distance}")  # Debug output

            if initial_volume_distance is None and distance < 30:
              initial_volume_distance = distance
            if initial_volume_distance is not None:
              # Adjust the range here to increase the sensitivity
              volume_level = np.interp(
                  distance,
                  [initial_volume_distance, initial_volume_distance + 150],
                  # Reduced range for higher sensitivity
                  [self.min_vol, self.max_vol])
              print(f"Setting volume to: {volume_level}")  # Debug output
              self.volume.SetMasterVolumeLevel(volume_level, None)
              if distance > initial_volume_distance + 50:
                initial_volume_distance = None
          # For right hand - brightness control
          elif handedness == "Right":
            thumb_tip = self.lm_list[4][1:]
            index_tip = self.lm_list[8][1:]
            distance = int(((index_tip[0] - thumb_tip[0])**2 +
                            (index_tip[1] - thumb_tip[1])**2)**0.5)
            if initial_brightness_distance is None and distance < 30:
              initial_brightness_distance = distance
            if initial_brightness_distance is not None:
              # Reduce the range to increase sensitivity for brightness adjustment
              brightness_level = np.interp(
                distance,
                [initial_brightness_distance, initial_brightness_distance + 200],
                # Reduced range for higher sensitivity
                [0, 100]`
              )
              sbc.set_brightness(int(brightness_level))
              if distance > initial_brightness_distance + 50:
                initial_brightness_distance = None
      # Display the live camera feed
      cv2.imshow("Img", img)
      if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit the loop if 'q' is pressed
        break
    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
  gesture_control = VolumeBrightnessGestureControl()
  gesture_control.run()
