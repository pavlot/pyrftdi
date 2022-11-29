import logging
from time import sleep

from pyftdi.spi import SpiController, SpiGpioPort
from pyRFTdi.Rfm75ConfigController import Rfm75ConfigController

from pyRFTdi.Rfm75Enums import Rfm75Command
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Registers import Rfm75Registers


class FtdiRfm75Controller:
    """This class intended to control RFM75(73) modules with SPI and GPIO ports"""

    def __init__(self, port: SpiController, gpio: SpiGpioPort, ce_pin: int, register_controller: Rfm75RegisterController):
        """Constructor

        :param port: SpiController Instance of SpiController interface which used to communicate with module
        :param gpio: SpiGpioPort Instance of SpiGpioPort interface which used to control CE pin state
        :param ce_pin: int GPIO pin number for CE pin
        :param register_controller: Rfm75RegisterController register controller used for low-level communication with module registers
        """
        self.__port = port
        self.__gpio = gpio
        self.__ce_pin = ce_pin
        self.__gpio.set_direction(1 << ce_pin, 1 << ce_pin)
        self.ce_off()

        self._register_controller = register_controller
        self.config_ctrl = Rfm75ConfigController(self._register_controller)

        # Event handlers
        self.on_data_received = None  # Called when new data received by loop_receive

        self.__receive_loop_run = False
        self.__receive_loop_stopped = True

    def activate_features(self):
        logging.debug("Features activated")
        self.__port.write(Rfm75Command.ACTIVATE_FEATURES, True, True)

    def ce_on(self) -> int:
        """Set pin CE to HIGH value
        
        :return:  GPIO state after operation
        
        """
        pins = self.__gpio.read()
        pins |= 1 << self.__ce_pin
        self.__gpio.write(pins)
        return self.__gpio.read()

    def ce_off(self) -> int:
        """Set pin CE to LOW value
        
        :return:  GPIO state after operation
        
        """
        pins = self.__gpio.read()
        pins &= ~((1 << self.__ce_pin))
        self.__gpio.write(pins)
        return self.__gpio.read()

    def get_chip_id(self) -> bytearray:
        return self._register_controller.read_register(Rfm75Registers.B1_CHIP_ID)

    def read_rx_payload_len(self) -> int:
        """Retrieve available payload length. Could be used to determinate whether new data available in RX buffer
        
        :return:  number of bytes available for the top R_RX_PAYLOAD in the RX FIFO
        
        """
        result = int(self.__port.exchange([Rfm75Command.R_RX_PL_WID], 1)[0])
        logging.debug("R_RX_PAYLOAD length is {}".format(result))
        return result

    def read_rx_payload(self, len: int) -> bytearray:
        """Retrieve given amount of bytes from RX buffer.
        
        :return:  R_RX_PAYLOAD as bytearray
        
        """
        return self.__port.exchange([Rfm75Command.R_RX_PAYLOAD], len, True, True)

    def is_connected(self):
        bank_0_status = self._register_controller.read_register(
            Rfm75Registers.STATUS)
        bank_1_status = self._register_controller.read_register(
            Rfm75Registers.B1_STATUS)
        result = (bank_0_status[0] ^ bank_1_status[0]) > 0
        logging.info("Is RFMx chip connected: {}".format(result))
        return result

    def get_register_controller(self):
        return self._register_controller

    def power_up(self):
        """" Set POWER_UP mode for RFx module
        
        :return:  bytearray representation of Rfm75Registers.CONFIG register
        
        """
        logging.info("RFx module power up")
        return self._register_controller.set_register_bit(Rfm75Registers.CONFIG, 1)

    def power_down(self):
        """ Set POWER_DOWN mode for RFx module
        
        :return:  bytearray representation of Rfm75Registers.CONFIG register
        
        """
        logging.info("RFx module power down")
        return self._register_controller.unset_register_bit(Rfm75Registers.CONFIG, 1)

    def set_mode_tx(self):
        self._register_controller.unset_register_bit(
            Rfm75Registers.CONFIG, 0x00)
        self._register_controller.write_register(Rfm75Registers.STATUS, [0x70])
        self.__port.exchange([Rfm75Command.FLUSH_TX], True, True)

    def set_mode_rx(self):
        self._register_controller.set_register_bit(Rfm75Registers.CONFIG, 0x00)

    def write_tx_payload(self, payload: bytearray, ack_send: bool = False):
        """Send data to the air.

        :param payload: data to be sent. It's length must not exceed PAYLOAD size
        :param ack_send: has no meaning when AA disabled, but if any AA enabled, this parameter allow to control which command actual used for data transfer
        
        """
        command = Rfm75Command.W_TX_PAYLOAD
        if self.config_ctrl.pipe_ctrl.is_auto_acknowledge_enabled() and not ack_send:
            command = Rfm75Command.W_TX_PAYLOAD_NO_ACK
        self.ce_off()
        self.__port.exchange([command], 0, True, False)
        for pld_byte in payload:
            self.__port.exchange([pld_byte], 0, False, False)
        self.__port.exchange([], 0, False, True)
        self.ce_on()
        # This delay is to guarantee that we do not stay in TX mode longer than allowed by datasheet
        sleep(0.002)
        self.ce_off()

    def flush_rx(self):
        self.__port.exchange([Rfm75Command.FLUSH_RX], True, True)

    def __loop_receive(self):
        while(self.__receive_loop_run):
            payload_len = self.read_rx_payload_len()
            if(payload_len > 0):
                logging.debug("Data received: {}".format(
                    self.read_rx_payload(payload_len).hex()))
                if self.on_data_received:
                    self.on_data_received(
                        payload_len, self.read_rx_payload(payload_len))
        self.__receive_loop_stopped = True

    def start_loop_receive(self):
        self.__receive_loop_stopped = False
        self.__receive_loop_run = True
        self.__loop_receive()

    def stop_loop_receive(self):
        self.__receive_loop_run = False
        return self.__receive_loop_stopped
