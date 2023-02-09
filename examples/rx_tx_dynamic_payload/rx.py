import logging

from pyftdi.spi import SpiController
from struct import *
from pyRFTdi.Rfm75Enums import Rfm75AddressWidth, Rfm75CRCLen, Rfm75Command
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Controller import FtdiRfm75Controller
from pyRFTdi.Rfm75Registers import Rfm75Register, Rfm75Registers

##################################################################################################
# Config
##################################################################################################

FTDI_URL = 'ftdi://ftdi:232h:555551/1'  # Url for ftdi chip, used to control RX
CE_PIN = 7                              # FTDI pin used to as CE for RFM device

PIPE_NO = 0                             # Pipe number used to receive data
ADDR_WIDTH = Rfm75AddressWidth.ADDR_5   # How many bytes used for address
PIPE_ADDR = b'\x11\x22\x33\x22\x11'     # Addres for selected pipe
RF_CHANNEL = 0x04                       # Operating Rf Channel
DATA_RATE = '1Msps'                     # Transfer speed

##################################################################################################
# End of config
##################################################################################################

logging.basicConfig(level=logging.INFO)
logging.info("RX part started")


ftdi_ctrl = SpiController(cs_count=2)  # spi
ftdi_ctrl.configure(FTDI_URL)  # Assuming there is only one FT232H.

ftdi_port = ftdi_ctrl.get_port(cs=0, freq=8E6)
ftdi_gpio = ftdi_ctrl.get_gpio()

reg_controller = Rfm75RegisterController(ftdi_port)

logging.info("----  Starting module initialisation ------")

controller = FtdiRfm75Controller(ftdi_port, ftdi_gpio, CE_PIN, reg_controller)

if(not controller.is_connected()):
    logging.error("RFMx controller not found, exit")
    exit(1)

logging.info("Chip id: {}".format(controller.get_chip_id().hex()))
controller.config_ctrl.reset_config()
controller.config_ctrl.set_rf_channel(RF_CHANNEL)
controller.config_ctrl.set_lna_gain_low()
controller.config_ctrl.chip_init(DATA_RATE)

controller.config_ctrl.enable_dynamic_payload()
controller.config_ctrl.enable_payload_ack()
controller.activate_features()

controller.config_ctrl.set_address_width(ADDR_WIDTH)

# Configure PIPE
controller.config_ctrl.pipe_ctrl.enable_pipe(PIPE_NO)
controller.config_ctrl.pipe_ctrl.enable_pipe_dynamic_payload(PIPE_NO)
controller.config_ctrl.pipe_ctrl.set_rx_pipe_address(PIPE_NO, PIPE_ADDR)
controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge()
controller.config_ctrl.pipe_ctrl.enable_pipe_auto_acknowledge(PIPE_NO)
controller.config_ctrl.crc_ctrl.set_crc_len(Rfm75CRCLen.CRC_2)
controller.config_ctrl.crc_ctrl.enable_crc()

controller.set_mode_rx()

controller.power_up()
controller.ce_on()

logging.info("----  Module initialisation done ------")
logging.info("----  Starting main receive loop ------")
try:
    while(1):
        payload_len = controller.read_rx_payload_len()
        if(payload_len > 0):
            logging.info("Data received: {}".format(controller.read_rx_payload(payload_len).hex()))
except KeyboardInterrupt:
    logging.info("----  Keyboard interrupt, shutdown ------")
    controller.ce_off()
    controller.power_down()
