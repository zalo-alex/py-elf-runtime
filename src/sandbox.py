from src.utils import debug, debug_value, to_int
from src.registers import Registers
from src.syscall import Syscalls

#
#   PREFIXES
#

class Prefix:
    mask = 0b11111111
    match = 0x0

    def __init__(self, byte):
        self.byte = byte

    @classmethod
    def check(cls, byte):
        return (byte & cls.mask) == cls.match
    
    @staticmethod
    def find_prefix(byte):
        for cls in Prefix.__subclasses__():
            if cls != NoPrefix and cls.check(byte):
                return cls(byte)
        return None
    
    @classmethod
    def __getattr__(cls, key):
        try:
            return getattr(cls, key)
        except:
            return None

class NoPrefix(Prefix):
    mask = 0b00000000

class REX(Prefix):
    mask = 0b11110000
    match = 0b01000000

    def __init__(self, byte):
        self.byte = byte
        self.w = self.byte & 0b00001000
        self.r = self.byte & 0b00000100
        self.x = self.byte & 0b00000010
        self.b = self.byte & 0b00000001

class _0F(Prefix):
    match = 0b00001111

class _F3(Prefix):
    match = 0b11110011

#
#   INSTRUCTIONS
#

class Instruction:
    # Primary opcode matching
    # po_mask = 0b0 if no po
    po_mask = 0b11111111
    po = 0x0
    
    p = NoPrefix
    
    def __init__(self, prefix, op, runtime):
        self.prefix = prefix
        self.op = op
        self.rt = runtime
        
    def execute(self):
        raise NotImplementedError
    
    @classmethod
    def check(cls, prefix, op):
        return (op & cls.po_mask) == cls.po and \
            (not prefix or (prefix.byte & cls.p.mask) == cls.p.match)
    
    @staticmethod
    def find_instruction(prefix, op, runtime):
        for cls in Instruction.__subclasses__():
            if cls.check(prefix, op):
                return cls(prefix, op, runtime)
        return None
    
# Ref: https://ref.x86asm.net/coder64.html
# Class names: mnemonic_po
class MOV_B8(Instruction):
    po_mask = 0b11111000
    po = 0xb8
    def execute(self):
        r = self.op & 0b00000111
        Registers.set(r, self.rt.read(8))

class MOV_C7(Instruction):
    po = 0xc7
    def execute(self):
        modrm = self.rt.read(1)
        register = modrm & 0b00000111
        if self.prefix.w:
            imm = self.rt.read(4)
        else:
            imm = self.rt.read(2)
        Registers.set(register, imm)

class SYSCALL_05(Instruction):
    po = 0x05
    p = _0F
    def execute(self):
        Syscalls.run(self.rt)

class XOR_31(Instruction):
    po = 0x31
    def execute(self):
        modrm = self.rt.read(1)
        r1 = modrm & 0b00111000 >> 3
        r2 = modrm & 0b00000111
        Registers.set(r1, r1 ^ r2)

class ENDBR64(Instruction):
    # Ignore instruction
    po = 0x0F
    p = _F3
    def execute(self): 
        self.rt.read(2)

#
#   RUNTIME CORE CLASS
#

class Runtime:
    
    def __init__(self, f, rip, byteorder):
        self.f = f
        self.rip = rip
        self.byteorder = byteorder
        
        self.f.seek(rip)
    
    def read(self, size):
        self.rip += size
        return to_int(self.f.read(size), self.byteorder)

    def access(self, addr, size):
        self.f.seek(addr)
        d = self.f.read(size)
        self.f.seek(self.rip)
        return d
    
    def execute(self):        
        while True:
            self.parse_instruction()

    def parse_instruction(self):
        byte = self.read(1)

        prefix = Prefix.find_prefix(byte)
        if prefix:
            op = self.read(1)
        else:
            op = byte

        ins = Instruction.find_instruction(prefix, op, self)
        
        if ins is None:
            raise Exception(f"Unknown instruction {hex(op)} at {hex(self.f.tell() - 1)}")
        
        ins.execute()