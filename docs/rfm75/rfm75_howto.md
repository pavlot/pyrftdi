# Connect

# Simple TX/RX
[rx_tx example](../../examples/rx_tx/) demonstrate simplest way to transfer data between two RFM devices using FTDI.
In this example there are two scripts: [rx.py](../../examples/rx_tx/rx.py) to receive data and [tx.py](../../examples/rx_tx/tx.py) to transfer data
Each script runs infinite loop to transmit/receive data. Payload is 5 byte length and contains magic sequence "cafeb0ba" ended with counter

## Configuration parameters
After RFM device wired to FTDI, you need to provide URL for FTDI device.
Check [pyFTDI documentation](https://eblot.github.io/pyftdi/urlscheme.html) how to obtain correct url.

For both rx and tx scripts this value controlled by varible
```python
FTDI_URL = 'ftdi://ftdi:232h:555551/1'  # Url for ftdi chip, used to control RX
```
Make sure to use correct URL's for TX and RX script. This example assume that rx and tx devices connected to different FTDI boards.

Next parameter required for pairing:
```python 
CE_PIN = 7                              # FTDI pin used to as CE for RFM device
```
This is [FTDI GPIO](https://eblot.github.io/pyftdi/api/spi.html#gpios) pin used to send CE signal to RFM device

Rest of parameters are related to RFM chip config and explained in comments

```python
PIPE_NO = 0                             # Pipe number used to receive data
ADDR_WIDTH = Rfm75AddressWidth.ADDR_5   # How many bytes used for address
PIPE_ADDR = b'\x11\x22\x33\x22\x11'     # Addres for selected pipe
RF_CHANNEL = 0x02                       # Operating Rf Channel
DATA_RATE = '250ksps'                   # Transfer speed
PAYLOAD_SIZE = 0x05                     # Static payload size up to 32b
```
## Configure chip to transmit/receive data
Simplest mode to transmit data it is when transmitter send data into the air and do not care whether it was received. Typical configuration is:

TX Part
```python
controller = FtdiRfm75Controller(ftdi_port, ftdi_gpio, CE_PIN, reg_controller)

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
controller.config_ctrl.set_tx_address(TX_ADDR)
# Do not pollute air with our RF waves 
controller.config_ctrl.set_tx_power(Rfm75TxPower.TX_PWR_LOW)

# In this mode tranceiver does not care whether packet was received by target device
controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge()

# Enable hardware CRC calculation and set it to 2 bytes
controller.config_ctrl.crc_ctrl.set_crc_len(Rfm75CRCLen.CRC_2)
controller.config_ctrl.crc_ctrl.enable_crc()

# Switch to TX mode
controller.set_mode_tx()
# Turn on RFM power. Note this is standby mode. Data is not transmitted until CE enabled and data present in TX buffer. 
controller.power_up()
```
After this call
```python
controller.write_tx_payload(payload)
```
to send payload.

Receiver initialisation almost the same as for transmiter, except few details:

First pipe should be configured:
```python
controller.config_ctrl.pipe_ctrl.enable_pipe(PIPE_NO)   # Enable required pipe
controller.config_ctrl.pipe_ctrl.set_rx_pipe_address(PIPE_NO, PIPE_ADDR)    # Set pipe address, RFM dewice has 5 pipes, each must have uniq address
controller.config_ctrl.pipe_ctrl.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)   # Static payload size
controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge() # Disable AA
```
After initialisation done chip must be set to RX mode using following calls:
```python
controller.set_mode_rx()
controller.power_up()
controller.ce_on()
```
Remember about `ce_on()` after `power_up()` - this will instruct RFP device to listen air for incoming data.

When data awailable `controller.read_rx_payload_len()` return non zero walue, so typical receive loop will be like:
```python
payload_len = controller.read_rx_payload_len()
if(payload_len > 0):
    logging.info("Data received: {}".format(controller.read_rx_payload(payload_len).hex()))

```