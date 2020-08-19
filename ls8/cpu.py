"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 0xF4
        self.running = True
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP

    def handle_LDI(self, a, b):
        self.reg[a] = b
        self.pc += 3

    def handle_PRN(self, a, b):
        print(self.reg[a])
        self.pc += 2

    def handle_HLT(self, a, b):
        self.running = False

    def handle_MUL(self, a, b):
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3
    
    def handle_PUSH(self, a, b):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.reg[a])
        self.pc += 2

    def handle_POP(self, a, b):
        self.reg[a] = self.ram_read(self.reg[7])
        self.reg[7] += 1
        self.pc += 2

    def load(self):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        address = 0
        filename = sys.argv[1]

        if filename:
            with open(filename) as f:
                for line in f:
                    line = line.split('#')
                    if line[0] == '':
                        continue

                    self.ram[address] = int(line[0], 2)
                    address += 1

        else:
            print('missing command line argument')
            sys.exit(0)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        # elif op == "MUL":
        #     self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            instruction = self.ram[self.pc]
            operand_a = self.ram[self.pc+1]
            operand_b = self.ram[self.pc+2]

            # if instruction == 0b00000001:  # HLT
            #     running = False

            # elif instruction == 0b10000010:  # LDI
            #     self.ram_write(operand_a, operand_b)
            #     self.pc += 2

            # elif instruction == 0b01000111:  # PRN
            #     print(self.ram_read(operand_a))
            #     self.pc += 1

            # elif instruction == 0b10100010:  # MUL
            #     self.ram_write(
            #         operand_a, (self.ram[operand_a] * self.ram[operand_b]))
            #     self.pc += 2

            # self.pc += 1

            try:
                self.branchtable[instruction](operand_a, operand_b)

            except:
                raise Exception(f'unknown instruction {instruction} at address {self.pc}')

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr


# test code
# cpu = CPU()

# cpu.load()
# cpu.run()