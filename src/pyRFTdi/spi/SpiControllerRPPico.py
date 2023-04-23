import logging
from pyRFTdi.spi.SpiController import SpiController

class SpiControllerRPPico(SpiController):
    def __init__(self, spi, cs_pin):
        self.__spi = spi
        self.__cs_pin = cs_pin

    def exchange(self, out: bytearray = b'',
                 readlen: int = 0, start: bool = True, stop: bool = True) -> bytes:
        """Perform an exchange or a transaction with the SPI slave

           :param out: data to send to the SPI slave, may be empty to read out
                       data from the slave with no write.
           :param readlen: count of bytes to read out from the slave,
                       may be zero to only write to the slave
           :param start: whether to start an SPI transaction, i.e.
                        activate the /CS line for the slave. Use False to
                        resume a previously started transaction
           :param stop: whether to desactivete the /CS line for the slave.
                       Use False if the transaction should complete with a
                       further call to exchange()
           :return: an array of bytes containing the data read out from the
                    slave
        """
        write_buffer = bytearray(out)
        read_buffer = bytearray([0] * readlen)
        
        if (start):
            self.__cs_pin(0)
        try:
            logging.debug("Write buffer: {}".format(write_buffer.hex()))
            self.__spi.write(write_buffer)
            self.__spi.readinto(read_buffer)   
        finally:
            if (stop):
                self.__cs_pin(1)
        return read_buffer


    def write(self, out:  bytearray,
              start: bool = True, stop: bool = True, droptail: int = 0) \
            -> None:
        """Write bytes to the slave

           :param out: data to send to the SPI slave, may be empty to read out
                       data from the slave with no write.
           :param start: whether to start an SPI transaction, i.e.
                        activate the /CS line for the slave. Use False to
                        resume a previously started transaction
           :param stop: whether to desactivete the /CS line for the slave.
                        Use False if the transaction should complete with a
                        further call to exchange()
           :param droptail: ignore up to 7 last bits (for non-byte sized SPI
                               accesses)
        """
        out = bytearray(out)
        if (start):
            self.__cs_pin(0)
        try:
            self.__spi.write(out)
        finally:
            if (stop):
                self.__cs_pin(1)
