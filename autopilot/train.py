"""

    Utils for generating training data

"""

import os
import re
import time
import hashlib
import datetime
import sys
from PIL import Image, ImageOps
import keyboard
import cv2 as cv

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.exceptions import TrainException
from autopilot.screen import stream_local_game_screen

from ets2_telemetry.truck_values import TruckValues
from ets2_telemetry import TelemetryReader

from scripts.angle_rotation import angle_rotation_from_map
from scripts.to_numpy import to_numpy

class _ConfigType(type):
    def __getattr__(self, attr):
        raise TrainException('Invalid configuration: %s' % attr)
    
class Config(object):

    """
        Default configuration.
        To use a custom configuration you need to look into the class

        :attr BOX: 'screen.Box' object indicating capture area.
        :attr DATA_PATH: CSV file path.
        :attr IMG_PATH: Image file path.
        :attr IMG_EXT: Image file extension.
        :attr FILE_CSV_NAME: Unique image identifier
        :attr DEFAULT_FPS: Default target fps for screen capture.
        :attr WAIT_KEYPRESS: Button to stop or start saving data
        :attr DEBUG: If this is True, write debug msg print.
    """
    
    __metaclass__ = _ConfigType
    BOX = None
    DATA_PATH = os.path.join('D:\Projects\data_autopilot', 'csv')
    IMG_PATH = os.path.join('D:\Projects\data_autopilot', 'img', 'raw')
    IMG_EXT = 'jpg'
    FILE_CSV_NAME = 'autopilot_data'
    DEFAULT_FPS = 5


def save_image_file_RGB(file_csv_name, image, is_mirror = False):

    """
    
        Image saving function. Format RGB.

    """

    # filename image example: '{file_csv_name}_2024_05_01_12_10_30_10.jpg'
    filename = file_csv_name + '_' + re.sub(
        '[-:.]', '_', datetime.datetime.now().isoformat('_')[:-4]) + \
        '.' + _global_config.IMG_EXT
    
    if is_mirror:
        parts = filename.split('.')
        filename = '.'.join([parts[0], '_mirror', parts[1]])

    image.save(os.path.join(_global_config.IMG_PATH, filename))

    return filename


def write_in_csv(data):

    """
    
        Function of saving training data to a table CSV.
    
    """

    f = os.path.join(_global_config.DATA_PATH, _global_config.FILE_CSV_NAME + '.csv')
    with open(f, 'a' if os.path.isfile(f) else 'w') as file_:

        image_filename, sensor_data = data

        values = [image_filename] + [str(x) for x in sensor_data.values()]
        data = ','.join(values)
        file_.write(data + '\n')

        # if self._data_seq % 10 == 0:
        #     _print('seq: %s, filename: %s, datetime: %s' %
        #         (
        #             self._data_seq,
        #             image_filename,
        #             str(datetime.datetime.now())
        #         )
        #     )


def dict_from_sensor_data(sensor_data):
    return {
        "steer": sensor_data.steer,
        "throttle": sensor_data.throttle,
        "brake": sensor_data.brake
    }


def print_sensor_data_dict(sensor_data_dict):
    for key, value in sensor_data_dict.items():
        print(key, ' --- ', value, end='     ')
    print()
    #print("------------------------------------------------\n")


def generate_training_data(config=Config):

    """
        Generate training data.
        :param config: Training configuration class
        
    """

    global _global_config
    _global_config = config

    _save_img_file = False

    # Check if data paths exist and are writable.
    if not os.access(config.DATA_PATH, os.W_OK):
        raise TrainException('Invalid data path: %s' % config.DATA_PATH)
    if not os.access(config.IMG_PATH, os.W_OK):
        raise TrainException('Invalid image path: %s' % config.IMG_PATH)

    streamer = stream_local_game_screen(
        box=config.BOX, default_fps=config.DEFAULT_FPS)

    fps_adjuster = FpsAdjuster()
    last_sensor_data = None

    telemetry_reader = TelemetryReader()
    truck_info = TruckValues()

    # Checking for the existence of a data file.
    # If it is not there, fill in the names of the columns.
    path_file_csv = os.path.join(_global_config.DATA_PATH, _global_config.FILE_CSV_NAME + '.csv')

    print(path_file_csv)
    print(f'Path file csv not exists - {not os.path.exists(path_file_csv)}')

    if not os.path.exists(path_file_csv):
        with open(path_file_csv, "w") as file_:
            # Add headers
            telemetry_reader.update_telemetry(truck_info)
            sensor_data_dict = dict_from_sensor_data(truck_info)
            sensor_data_dict['angle_path'] = 0
            sensor_header = ','.join(sensor_data_dict.keys())
            csv_header = 'img,' + sensor_header
            file_.write(csv_header + '\n')

    front_coord = (530, 375, 1150, 750)         # Front
    minimax_coord = (1325, 600, 1475, 750)      # Path in minimap
    navigator_coord = (1225, 635, 1590, 820)

    # Total number of recorded data and number of mirrored turns.
    total_img = 0
    mirror_img = 0
    MAX_ANGLE_NOT_MIRROR = 850

    while True:

        if keyboard.is_pressed('q'):
            _save_img_file = True
        if keyboard.is_pressed('e'):
            _save_img_file = False

        if(_save_img_file):
            if last_sensor_data is None:
                # Start generator
                image_data = next(streamer)
            else:
                image_data = streamer.send(
                    fps_adjuster.get_next_fps(last_sensor_data))

            telemetry_reader.update_telemetry(truck_info)

            sensor_data = truck_info
            last_sensor_data = sensor_data

            image = Image.fromarray(image_data, 'RGB')

            image_front = image.crop(front_coord)
            image_minimap_numpy = to_numpy(image.crop(minimax_coord))
            angle_path = angle_rotation_from_map(image_minimap_numpy)

            print(angle_path)

            if (angle_path != 0):

                sensor_data_dict = dict_from_sensor_data(truck_info)
                sensor_data_dict['angle_path'] = int(angle_path)
                #print_sensor_data_dict(sensor_data_dict)

                if (abs(sensor_data_dict['steer']) > MAX_ANGLE_NOT_MIRROR):
                    image_front_mirror = ImageOps.mirror(image_front)
                    sensor_data_dict_mirror = sensor_data_dict.copy()
                    sensor_data_dict_mirror['steer'] *= -1

                    mirror_img += 1
                    total_img += 1

                    img_filename = save_image_file_RGB(_global_config.FILE_CSV_NAME, image_front_mirror, is_mirror=True)
                    write_in_csv([img_filename, sensor_data_dict_mirror])

                img_filename = save_image_file_RGB(_global_config.FILE_CSV_NAME, image_front)
                write_in_csv([img_filename, sensor_data_dict])

                total_img += 1

                print(f'Total images - {total_img}, Mirror images - {mirror_img}, Save image - {_save_img_file}', end='\n\n')


class FpsAdjuster(object):

    """
    
        Adjust frames per second (FPS) depending on the rotation of the car's steering wheel.
        When driving with a slight turn of the steering wheel for more than 2 seconds, 
            the FPS drops by 2 times.

    """

    def __init__(self):

        """

            :param default_fps: Value from Config.
            :param adjust_factor: The coefficient at which to divide FPS.
            :param duration_threshold: The threshold value for how long the car is 
                    in motion right before the FPS drops. Calculated in seconds.
            :param max_straight_wheel_axis: The maximum amount of wheel rotation at 
                    which the car is considered to be moving straight.
            :param last_straight_time: Time of last movement of the car in a straight line.

        """

        self._default_fps = _global_config.DEFAULT_FPS
        self._adjust_factor = 2
        self._duration_threshold = 2
        self._max_straight_wheel_axis = 200
        self._last_straight_time = None

    def get_next_fps(self, sensor_data):

        """

            :param sensor_data: ets2_telemetry object.

        """

        going_straight = self._going_straight(sensor_data.steer)
        
        if self._last_straight_time is None:
            self._update_last_straight_time(going_straight)
            return self._default_fps

        straight_duration = time.time() - self._last_straight_time
        
        if going_straight and \
                straight_duration > self._duration_threshold:
            # Adjust fps
            return max(self._default_fps // self._adjust_factor, 1)
        else:
            self._update_last_straight_time(going_straight)
            return self._default_fps

    def _going_straight(self, wheel_axis):
        return abs(wheel_axis) < self._max_straight_wheel_axis

    def _update_last_straight_time(self, going_straight):
        if self._last_straight_time is None and going_straight:
            self._last_straight_time = time.time()
        elif not going_straight:
            self._last_straight_time = None
        # If last_controller_state is not None and going_straight, do nothing