import logging
from time import sleep
from pyftdi.spi import SpiController
from struct import *
from pyRFTdi.Rfm75Enums import Rfm75AddressWidth
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Controller import FtdiRfm75Controller
from pyRFTdi.Rfm75Registers import Rfm75Register, Rfm75Registers

logging.basicConfig(level=logging.INFO)
logging.info("TX part started")


ftdi_ctrl = SpiController(cs_count=2)  # spi
ftdi_ctrl.configure('ftdi://ftdi:232h:555552/1')  # Assuming there is only one FT232H.

ftdi_port = ftdi_ctrl.get_port(cs=0, freq=8E6)
ftdi_gpio = ftdi_ctrl.get_gpio()

reg_controller = Rfm75RegisterController(ftdi_port)

PIPE_NO = 0
CE_PIN = 7
PAYLOAD_SIZE = 0x05

logging.info("----  Starting module initialisation ------")

controller = FtdiRfm75Controller(ftdi_port, ftdi_gpio, CE_PIN, reg_controller)

if(not controller.is_connected()):
    logging.error("RFMx controller not found, exit")
    exit(1)

controller.reset_config()

print(controller.set_address_width(Rfm75AddressWidth.ADDR_5))
print("Pipe addr: {}".format(controller.set_rx_pipe_address(
    PIPE_NO, b'\x11\x22\x33\x22\x11').hex()))
controller.enable_pipe_auto_acknowledge(PIPE_NO)

controller.set_tx_address(b'\x11\x22\x33\x22\x11')

controller.chip_init('1Msps')

# Max TX power
reg_controller.set_register_bit(
         Rfm75Registers.RF_SETUP, 1)
reg_controller.set_register_bit(
         Rfm75Registers.RF_SETUP, 2)


controller.activate_features()

#reg_controller.write_register(Rfm75Register(0, 0x04, 1), [0x00]) #TODO check it


controller.enable_dynamic_acknowledge()

controller.enable_pipe(PIPE_NO)
controller.disable_dynamic_payload()
controller.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)

controller.enable_pipe_auto_acknowledge(PIPE_NO)
reg_controller.set_register_bit(Rfm75Registers.CONFIG, 2) # CRC 2 byte

controller.set_rf_channel(0x04)
controller.set_mode_tx()

controller.power_up()
counter = 0
try:
    while(1):
        logging.info("Status register before send: b{:b}".format(reg_controller.read_register(
            Rfm75Registers.STATUS)[0]))
        controller.write_tx_payload([0xCA, 0xFE, 0xB0, 0xBA, counter], True)
        counter += 1
        if(counter >= 0xFF):
            counter = 0
        logging.info("Status register after send: b{:b}".format(reg_controller.read_register(
            Rfm75Registers.STATUS)[0]))
        if(reg_controller.read_register_bit(Rfm75Registers.STATUS, 4)>0):
            logging.warning("MAX_RT detected, cleaning")
            reg_controller.set_register_bit(
                Rfm75Registers.STATUS, 4)
        reg_controller.set_register_bit(
            Rfm75Registers.STATUS, 5)

        sleep(1)
except KeyboardInterrupt:
    logging.info("----  Keyboard interrupt, shutdown ------")
    controller.ce_off()
    controller.power_down()
    