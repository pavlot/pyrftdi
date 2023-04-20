from pyRFTdi.Rfm75Registers import Rfm75Register, Rfm75Registers
from pyRFTdi.Rfm75Enums import Rfm75Command


class Rfm75RegisterController:

    def __init__(self, port):
        self.__port = port

    def set_register_bit(self, register: Rfm75Register, bit_num: int):
        bytes = self.read_register(register)
        val = int.from_bytes(bytes, 'little')
        val = val | (1 << bit_num)
        result = self.write_register(
            register, val.to_bytes(register.size, 'little'))
        return result

    def unset_register_bit(self, register: Rfm75Register, bit_num: int):
        bytes = self.read_register(register)
        val = int.from_bytes(bytes, 'little')
        val = val & ~(1 << bit_num)
        result = self.write_register(
            register, val.to_bytes(register.size, 'little'))
        return result

    def read_register_bit(self, register: Rfm75Register, bit_num: int)->int:
        bytes = self.read_register(register)
        val = int.from_bytes(bytes, 'little')
        val = (val & (1 << bit_num)) >> bit_num
        return val

    def set_bank_number(self, bank_number):
        if(self.get_bank_number() != bank_number):
            self.switch_bank_number()

    def get_bank_number(self):
        BANK_BIT_NUM = 7
        reg = self.__port.exchange(
            [Rfm75Registers.STATUS.addr], Rfm75Registers.STATUS.size, True, True)
        mask = 1 << BANK_BIT_NUM
        return (reg[0] & mask) >> BANK_BIT_NUM

    def switch_bank_number(self):
        self.__port.write([0x50, 0x53], True, True)

    def read_register(self, register: Rfm75Register):
        self.set_bank_number(register.bank)
        reg = self.__port.exchange([register.addr], register.size)
        return reg

    def write_register(self, register: Rfm75Register, values: bytearray) -> bytearray:
        """Write value to given register.
        :param register: Rfm75Register which defines address bank and register size
        :param values: Bytearray of values which represent register
        
:return:  new register value
        """
        if(len(values) > register.size):
            raise RuntimeError(
                "Values count [{}] does not fit register 0x{:02X} size: {} bytes.".format(
                    ", ".join(hex(value) for value in values),
                    register.addr,
                    register.size
                )
            )

        self.set_bank_number(register.bank)
        reg_write = register.addr | Rfm75Command.WRITE
        data = bytearray(reg_write.to_bytes(1, 'little'))
        data.extend(bytearray(values))
        # self.__port.write(reg_write.to_bytes(1, 'little'), True, False)
        # self.__port.exchange(values, 0, False, True)
        self.__port.exchange(data, 0, True, True)
        reg = self.__port.exchange([register.addr], register.size)
        return reg
