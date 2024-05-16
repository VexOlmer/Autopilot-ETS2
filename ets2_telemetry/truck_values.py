import struct
from . import AbstractDataClass


class TruckValues(AbstractDataClass):
    
    """
        Information about the truck.
        :attr steer: поворот руля
        :attr throttle: ускорение
        :attr brake: тормоз
    """

    steer = 0.0
    throttle = 0.0
    brake = 0.0
    clutch = 0.0
    wheelPositionZ = [0] * 16

    def update(self, memory_map):
        self.steer = int(struct.unpack("f", memory_map[972:976])[0] * 10000)
        self.throttle = int(struct.unpack("f", memory_map[976:980])[0] * 10000)
        self.brake = int(struct.unpack("f", memory_map[984:988])[0] * 10000)
        self.clutch = struct.unpack("f", memory_map[992:996])[0]
        self.wheelPositionZ = struct.unpack("16f", memory_map[1804:1868])
