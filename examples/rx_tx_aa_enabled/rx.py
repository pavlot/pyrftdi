import logging
from time import sleep

from pyftdi.spi import SpiController
from struct import *
from pyRFTdi.Rfm75Enums import Rfm75AddressWidth, Rfm75Command
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Controller import FtdiRfm75Controller
from pyRFTdi.Rfm75Registers import Rfm75Register, Rfm75Registers

##################################################################################################
# Config
##################################################################################################

FTDI_URL = 'ftdi://ftdi:232h:555551/1'  # Url for ftdi chip, used to control RX
PIPE_NO = 0                             # Pipe number used to receive data
PIPE_ADDR = b'\x11\x22\x33\x22\x11'     # Addres for selected pipe
CE_PIN = 7                              # FTDI pin used to as CE for RFMx device
PAYLOAD_SIZE = 0x05                     # Static payload size up to 32b

##################################################################################################
# End of config
##################################################################################################


logging.basicConfig(level=logging.INFO)
logging.info("RX part started")


ftdi_ctrl = SpiController(cs_count=2)  # spi
ftdi_ctrl.configure(FTDI_URL) 
ftdi_port = ftdi_ctrl.get_port(cs=0, freq=8E6)
ftdi_gpio = ftdi_ctrl.get_gpio()

reg_controller = Rfm75RegisterController(ftdi_port)

logging.info("----  Starting module initialisation ------")

controller = FtdiRfm75Controller(ftdi_port, ftdi_gpio, CE_PIN, reg_controller)

if(not controller.is_connected()):
    logging.error("RFMx controller not found, exit")
    exit(1)

controller.reset_config()
controller.set_address_width(Rfm75AddressWidth.ADDR_5)
controller.set_rx_pipe_address(PIPE_NO, PIPE_ADDR)

controller.chip_init('1Msps')

reg_controller.set_register_bit(
         Rfm75Registers.RF_SETUP, 0)

controller.activate_features()
#reg_controller.write_register(Rfm75Register(0, 0x04, 1), [0x00]) #TODO check it


controller.enable_dynamic_acknowledge()

controller.enable_pipe(PIPE_NO)
controller.disable_dynamic_payload()
controller.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)

controller.enable_pipe_auto_acknowledge(PIPE_NO)
reg_controller.set_register_bit(Rfm75Registers.CONFIG, 2) # CRC 2 byte


controller.set_mode_rx()
controller.set_rf_channel(0x04)

controller.power_up()
controller.ce_on()

logging.info("----  Module initialisation done ------")
logging.info("----  Starting main receive loop ------")
try:
    while(1):
        payload_len = controller.read_rx_payload_len()
        if(payload_len > 0):
            logging.info("Received {} bytes: {}".format(payload_len, controller.read_rx_payload(payload_len).hex()))
            #sleep(1)
            #ftdi_port.exchange([Rfm75Command.FLUSH_RX], True, True)

except KeyboardInterrupt:
    logging.info("----  Keyboard interrupt, shutdown ------")
    controller.ce_off()
    controller.power_down()