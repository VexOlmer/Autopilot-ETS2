"""

Utils for generating training data

"""

# NOTE добавить включение/выключение записи данных на кнопку
# NOTE исправить баг с уменьшением fps на разницу руля (чет не робит)

import os
import re
import time
import hashlib
import datetime
import sys
from PIL import Image
import keyboard

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.exceptions import TrainException
from autopilot.screen import stream_local_game_screen

from ets2_telemetry.truck_values import TruckValues
from ets2_telemetry import TelemetryReader

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
    KEY_OFFNO = 'q'
    DEBUG = True


def _print(text):
    if _global_config.DEBUG:
        print(text)

_global_config = Config


def save_image_file(file_csv_name, image_data):

    """
    
        Image saving function.

    """

    # filename image example: '{file_csv_name}_2024_05_01_12_10_30_10.jpg'
    filename = file_csv_name + '_' + re.sub(
        '[-:.]', '_', datetime.datetime.now().isoformat('_')[:-4]) + \
        '.' + _global_config.IMG_EXT

    image = Image.fromarray(image_data, 'RGB')
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
        "Steer": sensor_data.steer,
        "Throttle": sensor_data.throttle,
        "Brake": sensor_data.brake
    }


def generate_training_data(config=Config):

    """
        Generate training data.
        :param config: Training configuration class
    """

    global _global_config
    _global_config = config

    # Check if data paths exist and are writable.
    if not os.access(config.DATA_PATH, os.W_OK):
        raise TrainException('Invalid data path: %s' % config.DATA_PATH)
    if not os.access(config.IMG_PATH, os.W_OK):
        raise TrainException('Invalid image path: %s' % config.IMG_PATH)

    streamer = stream_local_game_screen(
        box=config.BOX, default_fps=config.DEFAULT_FPS)
    
    # train_uid = config.TRAIN_UID
    # if train_uid is None:
    #     d = str(datetime.datetime.now()).encode('utf8')
    #     train_uid = hashlib.md5(d).hexdigest()[:8]

    fps_adjuster = FpsAdjuster()
    last_sensor_data = None

    telemetry_reader = TelemetryReader()
    truck_info = TruckValues()

    # Checking for the existence of a data file.
    # If it is not there, fill in the names of the columns.
    path_file_csv = os.path.join(_global_config.DATA_PATH, _global_config.FILE_CSV_NAME + '.csv')
    print(not os.path.exists(path_file_csv))
    if not os.path.exists(path_file_csv):
        with open(path_file_csv, "w") as file_:
            # Add headers
            telemetry_reader.update_telemetry(truck_info)
            sensor_data_dict = dict_from_sensor_data(truck_info)
            sensor_header = ','.join(sensor_data_dict.keys())
            csv_header = 'img,' + sensor_header
            file_.write(csv_header + '\n')

    while True:

        if last_sensor_data is None:
            # Start generator
            image_data = next(streamer)
        else:
            image_data = streamer.send(
                fps_adjuster.get_next_fps(last_sensor_data))

        telemetry_reader.update_telemetry(truck_info)
        sensor_data = truck_info
        last_sensor_data = sensor_data

        sensor_data_dict = dict_from_sensor_data(truck_info)

        img_filename = save_image_file(_global_config.FILE_CSV_NAME, image_data)
        write_in_csv([img_filename, sensor_data_dict])


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
        self._max_straight_wheel_axis = 0.005
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
            return max(self._default_fps / self._adjust_factor, 1)
        else:
            self._update_last_straight_time(going_straight)
            return self._default_fps

    def _going_straight(self, wheel_axis):
        return abs(int(wheel_axis)) < self._max_straight_wheel_axis

    def _update_last_straight_time(self, going_straight):
        if self._last_straight_time is None and going_straight:
            self._last_straight_time = time.time()
        elif not going_straight:
            self._last_straight_time = None
        # If last_controller_state is not None and going_straight, do nothing