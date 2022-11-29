import logging
from pyRFTdi.Rfm75CRCConfigController import Rfm75CRCConfigController
from pyRFTdi.Rfm75Enums import Rfm75AddressWidth, Rfm75TxPower
from pyRFTdi.Rfm75PipeConfigController import Rfm75PipeConfigController
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Registers import Rfm75Registers


class Rfm75ConfigController:
    def __init__(self, register_controller: Rfm75RegisterController):
        """Constructor

        :param register_controller: Rfm75RegisterController register controller used for low-level communication with module registers
        """
        self._register_controller = register_controller
        self.pipe_ctrl = Rfm75PipeConfigController(self._register_controller)
        self.crc_ctrl = Rfm75CRCConfigController(self._register_controller)

    def set_rf_channel(self, channel: int) -> int:
        """The RF channel frequency determines the center of the channel used by RFM75. The
        frequency is set by the RF_CH register in register bank 0 according to the following
        formula: F0= 2400 + RF_CH (MHz). The resolution of the RF channel frequency is 1MHz.
        return channel number set

        :param channel: Channel number to be set

        :return: Value stored in channel register
        """
        logging.info("RF channel set to {}".format(channel))
        return int(self._register_controller.write_register(
            Rfm75Registers.RF_CH, [channel])[0])

    def get_rf_channel(self) -> int:
        """ Get RF channel configured """
        return int(self._register_controller.read_register(Rfm75Registers.RF_CH)[0])

    def set_lna_gain_high(self) -> int:
        """Setup LNA gain to high
            0:Low gain(20dB down)
            1:High gain"""
        logging.info("LNA gain set to high")
        return int(self._register_controller.set_register_bit(Rfm75Registers.RF_SETUP, 0)[0])

    def set_lna_gain_low(self) -> int:
        """Setup LNA gain to high"""
        logging.info("LNA gain set to low")
        return int(self._register_controller.unset_register_bit(Rfm75Registers.RF_SETUP, 0)[0])

    def is_lna_gain_low(self) -> bool:
        """Return true if LNA gain is low"""
        return self._register_controller.read_register_bit(Rfm75Registers.RF_SETUP, 0) == 0

    def set_tx_power(self, power: Rfm75TxPower) -> Rfm75TxPower:
        logging.info("TX power bin value: {:02b}".format(power >> 1))
        bytes = self._register_controller.read_register(
            Rfm75Registers.RF_SETUP)
        val = int.from_bytes(bytes, 'little')
        val = val | power
        result = self._register_controller.write_register(
            Rfm75Registers.RF_SETUP, val.to_bytes(Rfm75Registers.RF_SETUP.size, 'little'))
        return result

    def get_tx_power(self) -> Rfm75TxPower:
        bytes = self._register_controller.read_register(
            Rfm75Registers.RF_SETUP)
        val = int.from_bytes(bytes, 'little')
        result = val & Rfm75TxPower.TX_PWR_HIGH
        return result

    def reset_config(self):
        """ Zeroing CONFIG register """
        self._register_controller.write_register(Rfm75Registers.CONFIG, [0x00])

    def set_address_width(self, width: Rfm75AddressWidth):
        """ Set address width for chip"""
        logging.info("Adress width binary value: {0:b}".format(width))
        return self._register_controller.write_register(Rfm75Registers.SETUP_AW, [width])

    def chip_init(self, speed: str):
        """Initialize chip with different magic numbers, required for proper operation

        :param speed: One of: "1Msps","2Msps","250ksps"
        """
        logging.info("Data rate is: {}".format(speed))
        if speed == "1Msps":
            self._register_controller.unset_register_bit(
                Rfm75Registers.RF_SETUP, 3)
            self._register_controller.unset_register_bit(
                Rfm75Registers.RF_SETUP, 5)
        if speed == "2Msps":
            self._register_controller.set_register_bit(
                Rfm75Registers.RF_SETUP, 3)
            self._register_controller.unset_register_bit(
                Rfm75Registers.RF_SETUP, 5)
        if speed == "250ksps":
            self._register_controller.unset_register_bit(
                Rfm75Registers.RF_SETUP, 3)
            self._register_controller.set_register_bit(
                Rfm75Registers.RF_SETUP, 5)

        B1_REG_04_VALUES = {
            "1Msps": [0xF9, 0x96, 0x82, 0x1B],
            "2Msps": [0xF9, 0x96, 0x82, 0xDB],
            "250ksps": [0xF9, 0x96, 0x8A, 0xDB]
        }
        B1_REG_05_VALUES = {
            "1Msps": [0x24, 0x06, 0x0F, 0xA6],
            "2Msps": [0x24, 0x06, 0x0F, 0xB6],
            "250ksps": [0x24, 0x06, 0x0F, 0xB6]
        }
        # Set of magic values provided by datasheet
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_00, [0x40, 0x4B, 0x01, 0xE2])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_01, [0xC0, 0x4B, 0x00, 0x00])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_02, [0xD0, 0xFC, 0x8C, 0x02])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_03, [0x99, 0x00, 0x39, 0x41])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_04, B1_REG_04_VALUES[speed])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_05, B1_REG_05_VALUES[speed])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_0C, [0x00, 0x12, 0x73, 0x00])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_0D, [0x36, 0xB4, 0x80, 0x00])
        self._register_controller.write_register(
            Rfm75Registers.B1_REG_0E, [0x41, 0x20, 0x08, 0x04, 0x81, 0x20, 0xCF, 0xF7, 0xFE, 0xFF, 0xFF])

    def enable_dynamic_payload(self, pipe_no):
        self._register_controller.set_register_bit(
            Rfm75Registers.FEATURE, 2)

    def disable_dynamic_payload(self):
        self._register_controller.unset_register_bit(
            Rfm75Registers.FEATURE, 2)  # Disable dynamic payload

    def enable_dynamic_acknowledge(self) -> bytearray:
        return self._register_controller.set_register_bit(Rfm75Registers.FEATURE, 0)

    def is_enabled_dynamic_acknowledge(self) -> bool:
        return self._register_controller.read_register_bit(Rfm75Registers.FEATURE, 0) > 0

    def disable_dynamic_acknowledge(self) -> bytearray:
        return self._register_controller.unset_register_bit(Rfm75Registers.FEATURE, 0)

    def set_tx_address(self, address: bytearray) -> bytearray:
        """Set address for TX operation.

        :param address: bytearray with address values. Length depends on value set by set_address_width() method for RX device
        
        :return:  address bytearray for TX
        """
        logging.info("TX address set to {}".format(address.hex()))
        return self._register_controller.write_register(Rfm75Registers.TX_ADDR, address)
