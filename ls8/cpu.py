"""CPU functionality."""

import sys
# instructions/opcopdes
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
# sprint codes
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # 256 bytes of memory
        self.ram = [0] * 256
        # 8 general-purpose registers
        self.reg = [0] * 8
        # program counter
        self.pc = 0
        # stack pointer sets R7 to 0xF4
        self.reg[7] = 0xF4
        # set the cpu to be running
        self.running = True
        # set up a branch table filled with handler functions for the instructions/opcodes
        self.branchtable = {}
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[ADD] = self.handle_ADD
        # sprint instructions/opcodes
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        # flag sets to 0
        self.fl = 0b00000000

    # function handlers for each instruction/opcode
    # takes operand_a & operand_b as arguments

    def handle_LDI(self, a, b):
        # set the value of register(a) to int(b)
        # move on 3 places
        self.reg[a] = b
        self.pc += 3

    def handle_PRN(self, a, b):
        # print value at stored register(a)
        # move on 2 places
        print(self.reg[a])
        self.pc += 2

    def handle_HLT(self, a, b):
        # halt running
        self.running = False

    def handle_MUL(self, a, b):
        # multiply value at register(a) with value at register(b)
        # move on 3 places
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3

    def handle_PUSH(self, a, b):
        # decrement the stack pointer
        # get the value from the register & put it on the stack at the SP
        # move on 2 places
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.reg[a])
        self.pc += 2

    def handle_POP(self, a, b):
        # add to the stack pointer
        # get the value from the stack pointed to by the SP & set to register(a)
        # move on 2 places
        self.reg[7] += 1
        self.reg[a] = self.ram_read(self.reg[7])
        self.pc += 2

    def handle_CALL(self, a, b):
        # push the ret address to the stack
        # set the counter to the subroutines address
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.pc + 2)
        self.pc = self.reg[a]

    def handle_RET(self, a, b):
        # pop the ret address from the stack to store in the counter
        self.pc = self.ram_read(self.reg[7])
        self.reg[7] += 1

    def handle_ADD(self, a, b):
        # add the value from register a to value at register b
        # move on 3 places
        self.reg[a] = self.reg[a] + self.reg[b]
        self.pc += 3

    # sprint handle functions
    # might have to add 2 or 3 to the self.pc
    def handle_CMP(self, a, b):
        # FL bits: 00000LGE
        # compare a & b registers
        # if equal, set the flag to 1
        if self.reg[a] == self.reg[b]:
            self.fl = 0b00000001
        
        # if reg a < reg b, set 'L' to 1
        if self.reg[a] < self.reg[b]:
            self.fl = 0b00000100
        
        # if reg a > reg b, set 'G' to 1
        if self.reg[a] > self.reg[b]:
            self.fl = 0b00000010
        # add to the counter 3 lines to move on           
        self.pc += 3

    def handle_JMP(self, a, b):
        # jump to the address stored in the given register (a)
        self.pc = self.reg[a]

    def handle_JEQ(self, a, b):
        # if the flag is equal (1), jump to the address stored in the given register (a)
        if self.fl & 0b00000001:
            self.pc = self.reg[a]
        else:
            # otherwise add 2 to the counter to carry on down
            self.pc += 2

    def handle_JNE(self, a, b):
        # if E flag equals 0, jump to the address stored in the given register(a)
        if (self.fl & 0b00000001) == 0:
            self.pc = self.reg[a]
        else:
            # else add 2 to the counter & carry on
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
        
        # address in the file to start at
        address = 0
        # for the second arg in the file 
        filename = sys.argv[1]
        if filename:
            # open the file
            with open(filename) as f:
                for line in f:
                    # split the lines at the '#' char
                    line = line.split('#')
                    # if nothing there, carry on
                    if line[0] == '':
                        continue

                    # get the line's binary code at each address
                    # add 1 to the address to move on
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
        # while the cpu is running
        while self.running:
            # stores the instruction
            instruction = self.ram[self.pc]
            # stores the bytes at pc+1 & pc+2
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
                # try the instruction/opcode using operand_a & operand_b
                self.branchtable[instruction](operand_a, operand_b)

            except:
                # if there's an exception, print the unknown instruction at the address
                raise Exception(
                    f'unknown instruction {instruction} at address {self.pc}')

    # mar = memory address register
    # mdr = memory data register
    def ram_read(self, mar):
        # accepts the address to read & returns the value stored there
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        # accepts a value to write & the address to write it to
        self.ram[mar] = mdr


# test code
# cpu = CPU()

# cpu.load()
# cpu.run()