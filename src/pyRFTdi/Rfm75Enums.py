class Rfm75AddressWidth:
    ADDR_3 = 0b01
    ADDR_4 = 0b10
    ADDR_5 = 0b11

class Rfm75Command:
    WRITE = 0x20
    ACTIVATE_FEATURES = [0x50, 0x73]
    R_RX_PL_WID = 0x60
    R_RX_PAYLOAD = 0x61
    W_TX_PAYLOAD = 0xA0
    W_TX_PAYLOAD_NO_ACK = 0xB0
    FLUSH_TX = 0xE1
    FLUSH_RX = 0xE2

class Rfm75CRCLen:
    CRC_1 = 0
    CRC_2 = 1

class Rfm75TxPower:
    TX_PWR_LOW = 0b000
    TX_PWR_1 = 0b010
    TX_PWR_2 = 0b100
    TX_PWR_HIGH = 0b110