# Connect

# Simple TX/RX
[rx_tx example](../../examples/rx_tx/) demonstrate simplest way to transfer data between two RFM devices using FTDI.
In this example there are two scripts: [rx.py](../../examples/rx_tx/rx.py) to receive data and [tx.py](../../examples/rx_tx/tx.py) to transfer data
Each script runs infinite loop to transmit/receive data. Payload is 5 byte length and contains magic sequence "cafeb0ba" ended with counter

## Configuration
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