from src.utils import debug, debug_value, to_int
from src.registers import Registers
from src.syscall import Syscalls

class Instruction:
    # Primary opcode matching
    # po_mask = 0b0 if no po
    po_mask = 0b11111111
    po = 0x0
    # Prefix matching
    # p_mask = 0b0 if no prefix
    p_mask = 0b11111111
    p = 0x0
    
    def __init__(self, prefix, op, sandbox):
        self.prefix = prefix
        self.op = op
        self.sb = sandbox
        
    def execute(self):
        raise NotImplementedError
    
    @classmethod
    def check(cls, prefix, op):
        return (op & cls.po_mask) == cls.po and (prefix & cls.p_mask) == cls.p
    
    @staticmethod
    def find_instruction(prefix, op, sandbox):
        for cls in Instruction.__subclasses__():
            if cls.check(prefix, op):
                return cls(prefix, op, sandbox)
        return None
 
#
#   ALL INSTRUCTIONS
#
    
# Ref: https://ref.x86asm.net/coder64.html
# Class names: mnemonic_po
class MOV_B8(Instruction):
    po_mask = 0b11111000
    po = 0xb8
    p = 0x48 # Invalid, for tests
    def execute(self):
        r = self.op & 0b00000111
        Registers.set(r, self.sb.read(8))

class MOV_C7(Instruction):
    po = 0xc7
    p = 0x48 # Invalid, for tests
    def execute(self):
        modrm = self.sb.read(1)
        register = modrm & 0b00000111
        Registers.set(register, self.sb.read(4))

class SYSCALL_05(Instruction):
    po = 0x05
    p = 0x0f
    def execute(self):
        Syscalls.run(self.sb)

#
#   SANDBOX CORE CLASS
#

class Sandbox:
    
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
            prefix = self.read(1)      
            
            if prefix not in [0x48, 0x0f, 0xf3]:
                raise Exception(f"Unknown prefix {hex(prefix)} at {hex(self.f.tell() - 1)}")
            
            self.parse_instruction(prefix)

    def parse_instruction(self, prefix):
        op = self.read(1)
        ins = Instruction.find_instruction(prefix, op, self)
        
        if ins is None:
            raise Exception(f"Unknown instruction {hex(op)} at {hex(self.f.tell() - 1)}")
        
        ins.execute()