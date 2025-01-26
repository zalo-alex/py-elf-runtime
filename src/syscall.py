from src.registers import Registers
from src.headers import p

import sys
import os

class Syscalls:
    
    @classmethod
    def run(cls, runtime):
        tell = runtime.f.tell()
        sc = Registers.get(Registers.RAX)
        calls = {
            0x1: cls.write,
            0x3C: cls.exit,
        }
        if sc in calls:
            calls[sc](runtime.f)
        else:
            print(f"Unknown syscall {sc}")
        runtime.f.seek(tell)
    
    @classmethod
    def write(cls, f):
        fileno = Registers.get(Registers.RDI)
        msg_len = Registers.get(Registers.RDX)
        f.seek(Registers.get(Registers.RSI) - p.paddr)
        msg = f.read(msg_len)
        os.write(fileno, msg)
    
    @classmethod
    def exit(cls, f):
        sys.exit(Registers.get(Registers.RDI))