"""

This module contains wrappers which help to read screen data

"""

import os
import ast
import time
import traceback
from sys import platform
from itertools import count
from subprocess import Popen, PIPE
import numpy as np
from mss import mss
import cv2
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.exceptions import ScreenException


class Box(object):
    
    """
        Universal rectangular area on the screen
    """
    
    # Global counter which is used to name each box uniquely
    _counter = count()

    def __init__(self, x1, y1, x2, y2, monitor=None):
        
        """
            (x1, y1) -> upper left point of the screen box
            (x2, y2) -> lower right point of the screen box

            (x1, y1)-----------------(x2, y1)
                |                        |
                |                        |
                |                        |
                |                        |
            (x1, y2)-----------------(x2, y2)

           :param monitor: to support multiple monitors
        """
        
        self._name = 'Box %s' % str(next(self._counter))
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._monitor = monitor

    @staticmethod
    def from_monitor(monitor):
        return Box(
            monitor.offset_x, monitor.offset_y,
            monitor.width, monitor.height
        )

    @staticmethod
    def from_tuple(tuple_):
        return Box(
            tuple_[0],
            tuple_[1],
            tuple_[2],
            tuple_[3]
        )

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._x2 - self._x1

    @property
    def height(self):
        return self._y2 - self._y1

    @property
    def channel(self):
        return 3

    @property
    def numpy_shape(self):
        return (self.height, self.width, self.channel)

    def to_tuple(self):
        return (self._x1, self._y1, self._x2, self._y2)


class Monitor(object):
    
    """
        This class holds monitor information.
    """
    
    def __init__(self, width, height, offset_x, offset_y, primary=False):
        
        """
            :param width:  Monitor width
            :param height: Monitor height
            :param offset_x, offset_y:
                If there are multiple monitors, other monitors expect for primary
                one have a offsets according to os display config.
            :param primary: Whether it is a primary monitor or not.
        """
        
        self._width = width
        self._height = height
        self._offset_x = offset_x
        self._offset_y = offset_y
        self._primary = primary

    @property
    def primary(self):
        return self._primary

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def offset_x(self):
        return self._offset_x

    @property
    def offset_y(self):
        return self._offset_y


class ScreenUtils(object):
    
    """
        Contains static methods for working with the screen
    """
    
    @staticmethod
    def select_screen_area():
        
        """
            Use opencv to select game window from entire screen and return
            'Box' object corresponding to game window.
        """

        monitors = ScreenUtils.get_local_monitors()
        # Use primary monitor to create box
        box = Box.from_monitor(monitors[0])
        local_grab = LocalScreenGrab(box)
        entire_screen = local_grab.grab()
        entire_screen = entire_screen.reshape(box.numpy_shape)

        window_name = 'select_screen_area'
        region = cv2.selectROI(window_name, entire_screen)
        
        return Box(
            region[0], region[1],
            region[0] + region[2], region[1] + region[3]
        )

    @staticmethod
    def get_local_monitors():
        
        """
            Use mss().monitors to get monitor information.
            mss().monitors[0] is a dict of all monitors together
            mss().monitors[N] is a dict of the monitor N (with N > 0)
        """

        mss_monitors = mss().monitors[1:]
        monitors = []
        
        for idx, elem in enumerate(mss_monitors):
            monitors.append(Monitor(
                elem['width'],
                elem['height'],
                elem['left'],
                elem['top'],
                idx == 0
            ))
        return monitors


class _LocalImpl(object):
    
    def __init__(self, box):
        self._box = box

    def read_screen(self):
        
        """
            Reads RGB screen data and returns corresponding 1 dimensional
            numpy array so that it can be reshaped later.
        """
        
        return self._post_process(
            self._read(self._box)
        )

    def _read(self, bounding_box):
        
        """
            Reads screen and returns raw RGB `bytearray`.
            :param bounding_box: Contain the coordinates of the desired area on the screen
        """
        
        raise NotImplementedError()

    def _post_process(self, raw):
        
        """
            Parses `bytearray` to `numpy.ndarray`
        """
        
        single_byte_uint = '|u1'
        return np.frombuffer(raw, dtype=single_byte_uint)


class MssImpl(_LocalImpl):
    def __init__(self, box):
        super(MssImpl, self).__init__(box)
        self._is_osx = platform == 'darwin'
        self._executor = mss()

        if self._is_osx:

            orig_func = self._executor.core.CGWindowListCreateImage

            def _hook(screen_bounds, list_option, window_id, image_option):
                norminal_resolution = 1 << 4
                return orig_func(
                    screen_bounds, list_option, window_id,
                    norminal_resolution
                )
            self._executor.core.CGWindowListCreateImage = _hook

    def _read(self, bounding_box):
        
        x1, y1, x2, y2 = bounding_box.to_tuple()
        width = x2 - x1
        height = y2 - y1

        monitor_dict = {
            'left': x1,
            'top': y1,
            'width': width,
            'height': height
        }

        adjust_needed = self._is_osx and width % 16 != 0
        
        if adjust_needed:
            
            """
                Fixing a bug related to not dividing the width by 16. 
                First, increase the dimensions, and then cut off the unnecessary.
            """

            adjusted_width = width + (16 - (width % 16))
            monitor_dict['width'] = adjusted_width

            adjusted_rgb_data = self._executor.grab(monitor_dict).rgb
            rgb_data = bytearray()
            num_channels = 3
            for idx in range(height):
                offset = idx * (adjusted_width * num_channels)
                rgb_data.extend(
                    adjusted_rgb_data[offset:offset + width * num_channels]
                )

            return rgb_data
        else:
            return self._executor.grab(monitor_dict).rgb


class ScreenGrab(object):
    
    """
        This class will capture screen inside this `Box`.
    """
    
    def __init__(self, box):        
        self._box = box

    @property
    def box(self):
        return self._box

    @box.setter
    def box(self, x):
        self._box = x

    def prepare(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    @property
    def ready(self):
        raise NotImplementedError()

    def grab(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def __repr__(self):
        return '<ScreenGrab [%s]>' % self._box.name


class LocalScreenGrab(ScreenGrab):
    def __init__(self, box, impl=MssImpl):
        self._impl = impl(box)

    def grab(self):
        return self._impl.read_screen()


def stream_local_game_screen(box=None, default_fps=10):
    
    """
        Convenient wrapper for local screen capture.

        :param box: If it's None, we first select game window area from screen
        and start streaming inside that box.
        :param default_fps: Target fps for screen capture.
    """
    
    if box is None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        subproc = Popen([
            'python', os.path.join(
                dir_path, '..', 'scripts/select_screen_area.py')
        ], stdout=PIPE)
        output, _ = subproc.communicate()

        try:
            box_tuple = ast.literal_eval(output.split('\n')[-2])
        except ValueError:
            traceback.print_exc()
            raise ScreenException('Failed to get screen area')

        box = Box.from_tuple(box_tuple)

    time_per_frame = 1.0 / default_fps
    local_grab = LocalScreenGrab(box)
    
    while True:
        start = time.time()

        screen = local_grab.grab()
        target_fps = yield screen.reshape(box.numpy_shape)
        if target_fps is not None:
            time_per_frame = 1.0 / target_fps

        execution_time = time.time() - start
        #print('FPS screen {}'.format(1 / execution_time))
        
        if execution_time > time_per_frame:
            # Too high fps. No need to sleep.
            pass
        else:
            time.sleep(time_per_frame - execution_time)