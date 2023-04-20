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
TX_ADDR = b'\x11\x22\x33\x22\x11'       # Addres where to transmit
RF_CHANNEL = 0x04                       # Operating Rf Channel
DATA_RATE = '250ksps'                   # Transfer speed
PAYLOAD_SIZE = 0x05                     # Static payload size up to 32b

##################################################################################################
# End of config
##################################################################################################
spi = SPI(0, baudrate=1000000, sck=Pin(2), mosi=Pin(3), miso=Pin(0))           # Create SPI peripheral 0 at frequency of 400kHz.
                                        # Depending on the use case, extra parameters may be required
                                        # to select the bus characteristics and/or pins to use.
cs_pin = Pin(1, mode=Pin.OUT, value=0)      # Create chip-select on pin 4.
ce_pin = Pin(4, mode=Pin.OUT, value=0)
spi_controller = SpiControllerRPPico(spi, cs_pin)

reg_controller = Rfm75RegisterController(spi_controller)

logging.info("----  Starting module initialisation ------")

controller = FtdiRfm75Controller(spi_controller, ce_pin, reg_controller)

if(not controller.is_connected()):                                      # Make sure we have chip connected
    logging.error("RFMx controller not found, exit")
    exit(1)

logging.info("Chip id: {}".format(controller.get_chip_id().hex()))      # Print connected chip ID
controller.config_ctrl.reset_config()                                   # Reset config to be sure we start from 0 walues
controller.config_ctrl.set_rf_channel(RF_CHANNEL)                       # Configure RF channel, be sure it is the same for transmitter and receiver
controller.config_ctrl.chip_init(DATA_RATE)                             # This is RFM magic init, most iportant to set data rate the same om transmitter and on receiver
# Activate features and disable any dynamic features
controller.activate_features()
controller.config_ctrl.disable_dynamic_payload()
controller.config_ctrl.disable_dynamic_acknowledge()

# Configure adress width up to 5 bytes
controller.config_ctrl.set_address_width(ADDR_WIDTH)
# Target receiver address
logging.info(controller.config_ctrl.set_tx_address(TX_ADDR).hex())
# Do not pollute air with our RF waves 
controller.config_ctrl.set_tx_power(Rfm75TxPower.TX_PWR_HIGH)

# In this mode tranceiver does not care whether packet was received by target device
controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge()

# Enable hardware CRC calculation and set it to 2 bytes
#controller.config_ctrl.crc_ctrl.set_crc_len(Rfm75CRCLen.CRC_2)
#controller.config_ctrl.crc_ctrl.enable_crc()
controller.config_ctrl.crc_ctrl.disable_crc()

# Switch to TX mode
controller.set_mode_tx()
# Turn on RFM power. Note this is standby II mode. Data is not transmitted until CE enabled and data present in TX buffer. 
controller.power_up()

logging.info("----  Module initialisation done ------")
logging.info("----  Starting main receive loop ------")

counter = 0
try:
    while(1):
        logging.debug("Status register before send: b{:b}".format(reg_controller.read_register(
            Rfm75Registers.STATUS)[0]))
        payload = bytearray([0xCA, 0xFE, 0xB0, 0xBA, counter])
        logging.info("Data transmitted {}".format(payload.hex()))
        controller.write_tx_payload(payload)
        counter += 1
        if(counter >= 0xFF):
            counter = 0
        logging.debug("Status register after send: b{:b}".format(reg_controller.read_register(
            Rfm75Registers.STATUS)[0]))
            
        #sleep(1)

except KeyboardInterrupt:
    logging.info("----  Keyboard interrupt, shutdown ------")
    controller.ce_off()
    controller.power_down()