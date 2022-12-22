import cv2
import numpy
import time


def gather_cv2_cameras(max_ind=20, img_size = 84):
    all_cv2_cameras = []
    for i in range(max_ind):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            camera = CV2Camera(cap, img_size)
            all_cv2_cameras.append(camera)
    return all_cv2_cameras


class CV2Camera:
    def __init__(self, cap, img_size = 84):
        self._cap = cap
        self.img_size = img_size
        self._serial_number = 'cv2'  # temporary

    def read_camera(self, enforce_same_dim=False):
        # Get a new frame from camera
        retval, frame = self._cap.read()
        if not retval: return None

        # Extract left and right images from side-by-side
        read_time = time.time()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, dsize=(self.img_size, self.img_size), interpolation=cv2.INTER_AREA)

        dict = {'array': img, 'shape': img.shape, 'type': 'rgb',
                  'read_time': read_time, 'serial_number': self._serial_number + '/rgb_image'}

        return [dict]

    def disable_camera(self):
        self._cap.release()
