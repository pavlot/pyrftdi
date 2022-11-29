import logging
from pyRFTdi.Rfm75Enums import Rfm75CRCLen
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Registers import Rfm75Registers


class Rfm75CRCConfigController:
    """Class to configure and controll device CRC handling"""
    def __init__(self, register_controller: Rfm75RegisterController):
        """Constructor
        :param register_controller: Rfm75RegisterController register controller used for low-level communication with module registers
        """
        self._register_controller = register_controller

    def set_crc_len(self, crc_len:Rfm75CRCLen):
        """Set CRC encoding schema
        :crc_len required length"""
        if crc_len == Rfm75CRCLen.CRC_2:
            logging.info("CRC encoding scheme 2 bytes")
            self._register_controller.set_register_bit(Rfm75Registers.CONFIG, 2)
        else:
            logging.info("CRC encoding scheme 1 byte")
            self._register_controller.unset_register_bit(Rfm75Registers.CONFIG, 2)

    def get_crc_len(self)->Rfm75CRCLen:
        """Get CRC encoding scheme
        
:return:  Rfm75CRCLen of used encoding"""
        val = self._register_controller.read_register_bit(Rfm75Registers.CONFIG, 2)
        return Rfm75CRCLen.CRC_2 if val > 0 else Rfm75CRCLen.CRC_1

    def enable_crc(self):
        """Enable CRC. NOTE Forced high if one of the bits in the EN_AA is high"""
        logging.info("CRC enabled")
        self._register_controller.set_register_bit(Rfm75Registers.CONFIG, 3)

    def disable_crc(self):
        """Enable CRC. NOTE Forced high if one of the bits in the EN_AA is high"""
        logging.info("CRC disabled")
        self._register_controller.unset_register_bit(Rfm75Registers.CONFIG, 3)

    def is_crc_enabled(self)->bool:
        """Return actuall state of CRC enabled bit"""
        return self._register_controller.read_register_bit(Rfm75Registers.CONFIG, 3) > 0 

