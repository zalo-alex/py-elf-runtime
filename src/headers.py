class EI:
    
    MAG = None
    CLASS = None
    DATA = None
    VERSION = None

class e:
    
    type = None
    machine = None
    version = None
    entry = None
    phoff = None
    shoff = None
    ehsize = None
    phentsize = None
    phnum = None
    shentsize = None
    shnum = None
    shstrndx = None

class p:
    
    type = None
    flags = None
    offset = None
    vaddr = None
    paddr = None
    filesz = None
    memsz = None

class sh:
    
    all = []
    names = []
    
    def __init__(self):
        self.name = None
        self.type = None
        self.flags = None
        self.addr = None
        self.offset = None
        self.size = None
        sh.all.append(self)