from src.utils import debug_value, debug

class Registers:
    
    all = [0] * 16
    
    RAX = 0b000
    RCX = 0b001
    RDX = 0b010
    RBX = 0b011
    RSP = 0b100
    RBP = 0b101
    RSI = 0b110
    RDI = 0b111
    
    @classmethod
    def set(cls, index, value):
        cls.all[index] = value
    
    @classmethod
    def get(cls, index):
        return cls.all[index]
    
    @classmethod
    def print(cls):
        debug(" @ Registers")
        for i in range(len(cls.all)):
            debug_value(f"R{i}", cls.all[i], 2)