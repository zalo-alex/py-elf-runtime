import sys

debug_mode = "debug" in sys.argv

def to_int(value, byteorder):
    return int.from_bytes(value, byteorder)

def debug(msg, level = 1):
    if not debug_mode:
        return
    
    t = "\t" * level
    print(f"{t}{msg}")

def debug_value(name, value, level = 2, info = None):
    if not debug_mode:
        return
    
    if type(value) == bytes:
        value = to_int(value, 'little')
    value = hex(value)
    t = "\t" * level
    if info:
        print(f"{t}{name}: {value}\t({info})")
    else:
        print(f"{t}{name}: {value}")