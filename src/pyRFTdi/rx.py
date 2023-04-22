import logging
from time import sleep
from machine import SPI, Pin
from pyRFTdi.spi.SpiControllerRPPico import SpiControllerRPPico
from struct import *
from pyRFTdi.Rfm75Enums import Rfm75AddressWidth, Rfm75CRCLen, Rfm75TxPower
from pyRFTdi.Rfm75RegisterController import Rfm75RegisterController
from pyRFTdi.Rfm75Controller import FtdiRfm75Controller
from pyRFTdi.Rfm75Registers import Rfm75Register, Rfm75Registers

logging.basicConfig(level=logging.INFO)
logging.info("TX part started")

##################################################################################################
# Config
##################################################################################################

FTDI_URL = 'ftdi://ftdi:232h:555552/1'  # Url for ftdi chip, used to control RX
CE_PIN = 7                              # FTDI pin used to as CE for RFM device

PIPE_NO = 0                             # Pipe number used to receive data
ADDR_WIDTH = Rfm75AddressWidth.ADDR_5   # How many bytes used for address
PIPE_ADDR = b'\x11\x22\x33\x22\x11'       # Addres where to transmit
RF_CHANNEL = 0x04                       # Operating Rf Channel
DATA_RATE = '250ksps'                   # Transfer speed
PAYLOAD_SIZE = 0x05                     # Static payload size up to 32b

##################################################################################################
# End of config
##################################################################################################
spi = SPI(0, baudrate=1000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))           # Create SPI peripheral 0 at frequency of 400kHz.
                                        # Depending on the use case, extra parameters may be required
                                        # to select the bus characteristics and/or pins to use.
cs_pin = Pin(17, mode=Pin.OUT, value=0)      # Create chip-select on pin 4.
ce_pin = Pin(20, mode=Pin.OUT, value=0)
spi_controller = SpiControllerRPPico(spi, cs_pin)

reg_controller = Rfm75RegisterController(spi_controller)

logging.info("----  Starting module initialisation ------")

controller = FtdiRfm75Controller(spi_controller, ce_pin, reg_controller)

if(not controller.is_connected()):
    logging.error("RFMx controller not found, exit")
    exit(1)

logging.info("Chip id: {}".format(controller.get_chip_id().hex()))
controller.config_ctrl.reset_config()
controller.config_ctrl.set_rf_channel(RF_CHANNEL)
controller.config_ctrl.set_lna_gain_high()
controller.config_ctrl.chip_init(DATA_RATE)

controller.config_ctrl.disable_dynamic_payload()
controller.config_ctrl.disable_dynamic_acknowledge()

controller.activate_features()

controller.config_ctrl.set_address_width(ADDR_WIDTH)

# Configure PIPE
controller.config_ctrl.pipe_ctrl.enable_pipe(PIPE_NO)
logging.info("PipeAddr after set: {}".format(controller.config_ctrl.pipe_ctrl.set_rx_pipe_address(PIPE_NO, PIPE_ADDR).hex()))
logging.info("PipeAddr: {}".format(controller.config_ctrl.pipe_ctrl.get_rx_pipe_address(PIPE_NO).hex()))
controller.config_ctrl.pipe_ctrl.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)
controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge()

# controller.config_ctrl.crc_ctrl.set_crc_len(Rfm75CRCLen.CRC_2)
# controller.config_ctrl.crc_ctrl.enable_crc()
controller.config_ctrl.crc_ctrl.disable_crc()

controller.set_mode_rx()

controller.power_up()
controller.ce_on()

logging.info("----  Module initialisation done ------")
logging.info("----  Starting main receive loop ------")
try:
    while(1):
        # payload_len = controller.read_rx_payload_len()
        # if(payload_len > 0):
        #     logging.info("Data received: {}".format(controller.read_rx_payload(payload_len).hex()))

        if(controller.is_rx_data_ready()):
            logging.info("Data received: {}".format(controller.read_rx_payload(5).hex()))
            controller.unset_rx_data_ready()

except KeyboardInterrupt:
    logging.info("----  Keyboard interrupt, shutdown ------")
    controller.ce_off()
    controller.power_down()
