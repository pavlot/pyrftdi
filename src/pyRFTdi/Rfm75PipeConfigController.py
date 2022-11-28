import logging
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Registers import Rfm75Registers


class Rfm75PipeConfigController:
    """Class to configure and controll device RX pipes"""
    def __init__(self, register_controller: Rfm75RegisterController):
        """Constructor
        :parameter register_controller: Rfm75RegisterController register controller used for low-level communication with module registers
        """
        self._register_controller = register_controller

    def enable_pipe(self, pipe_no: int) -> bytearray:
        """Enables RX pipe by given number
        :parameter pipe_no RX pipe number to enable
        :return Bytearray representing Rfm75Registers.EN_RXADDR value
        """
        logging.info("Pipe {} enabled".format(pipe_no))
        if(pipe_no < 0 or pipe_no > 5):
            raise RuntimeError(
                "Wrong pipe number: {}. Allowed values 0-5".format(pipe_no))
        return self._register_controller.set_register_bit(Rfm75Registers.EN_RXADDR, pipe_no)

    def disable_pipe(self, pipe_no: int):
        """Disables RX pipe by given number
        :parameter pipe_no RX pipe number to disable
        :return Bytearray representing Rfm75Registers.EN_RXADDR value
        """
        logging.info("Pipe {} disabled".format(pipe_no))
        if(pipe_no < 0 or pipe_no > 5):
            raise RuntimeError(
                "Wrong pipe number: {}. Allowed values 0-5".format(pipe_no))
        return self._register_controller.unset_register_bit(Rfm75Registers.EN_RXADDR, pipe_no)

    def disable_auto_acknowledge(self)->bytearray:
        """Disable AA for all pipes
        :return Bytearray representing Rfm75Registers.EN_AA value
        """
        logging.info("Auto acknowledge disabled")
        return self._register_controller.write_register(Rfm75Registers.EN_AA, [0])

    def is_auto_acknowledge_enabled(self)->bytearray:
        """
        :return Returns True in case if at least one PIPE has AA enabled
        """
        return self._register_controller.read_register(Rfm75Registers.EN_AA)[0] > 0

    def enable_pipe_auto_acknowledge(self, pipe_no:int)->bytearray:
        """Enables RX pipe auto acknowledge by given number
        :parameter pipe_no RX pipe number to enable auto acknowledge
        :return Bytearray representing Rfm75Registers.EN_AA value
        """
        logging.info("Auto acknowledge for pipe {} enabled".format(pipe_no))
        return self._register_controller.set_register_bit(Rfm75Registers.EN_AA, pipe_no)

    def disable_pipe_auto_acknowledge(self, pipe_no:int)->bytearray:
        """Disables RX pipe auto acknowledge by given number
        :parameter pipe_no RX pipe number to disable auto acknowledge
        :return Bytearray representing Rfm75Registers.EN_AA value
        """
        logging.info("Auto acknowledge for pipe {} disabled".format(pipe_no))
        return self._register_controller.unset_register_bit(Rfm75Registers.EN_AA, pipe_no)

    def get_pipe_auto_acknowledge(self, pipe_no:int)->bool:
        """Get RX pipe auto acknowledge by given number
        :parameter pipe_no RX pipe number to read auto acknowledge
        :return True if Pipe AA is set
        """
        logging.info("Auto acknowledge for pipe {} disabled".format(pipe_no))
        return self._register_controller.read_register_bit(Rfm75Registers.EN_AA, pipe_no) > 0

    def set_rx_pipe_address(self, pipe_no: int, address: bytearray) -> bytearray:
        """Set address for given pipe.
        :parameter pipe_no Pipe number in range 0-5 for which address is set
        :parameter address bytearray with address values. Length depends on value set by set_address_width() method
        :return address bytearray for given pipe
        """
        pipe_addr_registers = [
            Rfm75Registers.RX_ADDR_P0,
            Rfm75Registers.RX_ADDR_P1,
            Rfm75Registers.RX_ADDR_P2,
            Rfm75Registers.RX_ADDR_P3,
            Rfm75Registers.RX_ADDR_P4,
            Rfm75Registers.RX_ADDR_P5
        ]
        register = pipe_addr_registers[pipe_no]
        logging.info("RX_Pipe {} address set to {}".format(
            pipe_no, address.hex()))
        return self._register_controller.write_register(register, address)

    def get_rx_pipe_address(self, pipe_no: int) -> bytearray:
        """Get address for given pipe.
        :parameter pipe_no Pipe number in range 0-5 for which address is set
        :return address bytearray for given pipe
        """
        pipe_addr_registers = [
            Rfm75Registers.RX_ADDR_P0,
            Rfm75Registers.RX_ADDR_P1,
            Rfm75Registers.RX_ADDR_P2,
            Rfm75Registers.RX_ADDR_P3,
            Rfm75Registers.RX_ADDR_P4,
            Rfm75Registers.RX_ADDR_P5
        ]
        register = pipe_addr_registers[pipe_no]
        return self._register_controller.read_register(register)

    def set_rx_pipe_payload_width(self, pipe_no: int, width: int) -> bytearray:
        """Set payload width for given pipe in static mode.
        :parameter pipe_no Pipe number in range 0-5 for which payload width is set
        :parameter width Width in range 0-32
        :return Bytearray representation for Rfm75Registers.RX_PW_PX, where X = pipe_no
        """

        if(pipe_no < 0 or pipe_no > 5):
            raise RuntimeError(
                "Wrong pipe number: {}. Allowed values 0-5".format(pipe_no))
        if(width < 0 or width > 32):
            raise RuntimeError(
                "Wrong payload width {} for pipe {}. Allowed values 0-32".format(width, pipe_no))

        pipe_registers = [
            Rfm75Registers.RX_PW_P0,
            Rfm75Registers.RX_PW_P1,
            Rfm75Registers.RX_PW_P2,
            Rfm75Registers.RX_PW_P3,
            Rfm75Registers.RX_PW_P4,
            Rfm75Registers.RX_PW_P5
        ]
        register = pipe_registers[pipe_no]
        logging.info("Pipe {} RX payload width is {}".format(pipe_no, width))
        return self._register_controller.write_register(register, [width])

    def get_rx_pipe_payload_width(self, pipe_no: int) -> int:
        """Set payload width for given pipe in static mode.
        :parameter pipe_no Pipe number in range 0-5 for which payload width is set
        :parameter width Width in range 0-32
        :return Bytearray representation for Rfm75Registers.RX_PW_PX, where X = pipe_no
        """
        pipe_registers = [
            Rfm75Registers.RX_PW_P0,
            Rfm75Registers.RX_PW_P1,
            Rfm75Registers.RX_PW_P2,
            Rfm75Registers.RX_PW_P3,
            Rfm75Registers.RX_PW_P4,
            Rfm75Registers.RX_PW_P5
        ]
        register = pipe_registers[pipe_no]
        return int(self._register_controller.read_register(register)[0])

    def enable_pipe_dynamic_payload(self, pipe_no:int):
        logging.info("Enabling pipe {} dynamic_payload".format(pipe_no))
        self._register_controller.set_register_bit(Rfm75Registers.DYNPD, pipe_no)

    def is_enabled_pipe_dynamic_payload(self, pipe_no:int):
        return self._register_controller.read_register_bit(Rfm75Registers.DYNPD) > 0

    def disable_pipe_dynamic_payload(self, pipe_no:int):
        logging.info("Disabling pipe {} dynamic_payload".format(pipe_no))
        self._register_controller.set_register_bit(Rfm75Registers.DYNPD, pipe_no)
