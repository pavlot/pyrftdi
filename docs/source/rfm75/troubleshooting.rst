Troubleshooting
===============
If transmitted data is not received - first of all check that transmitter and receiver initialised with coupling parameters.
For example data will not be received if autoacknowledge turned ON on transmitter but disabled on receiver.

Logical analyzer should be used to debug SPI communication between RFM chip and FTDI board.

RFM chips sensitive to power quality. In case of stability issues make sure power supply provide stable 3.3v. Use filters if required.