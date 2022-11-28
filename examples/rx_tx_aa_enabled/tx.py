import logging
from time import sleep
from pyftdi.spi import SpiController
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
PIPE_ADDR = b'\x11\x22\x33\x22\x11'     # Addres for selected pipe, in tx mode 
                                        # requiered for AutoAcknowledge to work
RF_CHANNEL = 0x04                       # Operating Rf Channel
DATA_RATE = '250ksps'                   # Transfer speed
PAYLOAD_SIZE = 0x05                     # Static payload size up to 32b

##################################################################################################
# End of config
##################################################################################################


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
controller.config_ctrl.chip_init(DATA_RATE)
controller.activate_features()
controller.config_ctrl.disable_dynamic_payload()
controller.config_ctrl.disable_dynamic_acknowledge()

controller.config_ctrl.set_address_width(ADDR_WIDTH)
controller.config_ctrl.set_tx_address(TX_ADDR)

controller.config_ctrl.set_tx_power(Rfm75TxPower.TX_PWR_LOW)

controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge()

controller.config_ctrl.pipe_ctrl.enable_pipe(PIPE_NO)
controller.config_ctrl.pipe_ctrl.set_rx_pipe_address(PIPE_NO, PIPE_ADDR)
controller.config_ctrl.pipe_ctrl.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)
controller.config_ctrl.pipe_ctrl.enable_pipe_auto_acknowledge(PIPE_NO)

controller.config_ctrl.crc_ctrl.set_crc_len(Rfm75CRCLen.CRC_2)
controller.config_ctrl.crc_ctrl.enable_crc()
controller.set_mode_tx()

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
        controller.write_tx_payload(payload, True)
        counter += 1
        if(counter >= 0xFF):
            counter = 0
        logging.debug("Status register after send: b{:b}".format(reg_controller.read_register(
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