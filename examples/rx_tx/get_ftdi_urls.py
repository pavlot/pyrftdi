from pyftdi.eeprom import FtdiEeprom

# Instantiate an EEPROM manager
eeprom = FtdiEeprom()

# Select the FTDI device to access
eeprom.open('ftdi://ftdi:232h:555552/1')

# Change the serial number
eeprom.set_serial_number('555552')

# Commit the change to the EEPROM
eeprom.commit(dry_run=False)