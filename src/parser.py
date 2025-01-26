from src.utils import debug, to_int, debug_value
from src.headers import EI, e, p, sh
from src.sandbox import Sandbox

class Parser:
    
    def __init__(self, filename):
        self.f = open(filename, 'rb')
        self.byteorder = None
    
    def read(self, size):
        if not self.byteorder:
            return self.f.read(size)
        return to_int(self.f.read(size), self.byteorder)
        
    def parse(self):
        
        #
        #   ELF Header
        #
        
        EI.MAG = self.read(4)
        
        if EI.MAG != b"\x7fELF":
            print("Not an ELF file")
            return
        
        EI.CLASS = self.read(1)
        EI.DATA = self.read(1)
        EI.VERSION = self.read(1)
        
        self.byteorder = 'little' if EI.DATA == b"\x01" else 'big'
        
        debug(" # EI HEADER")
        
        debug_value("EI_MAG", EI.MAG)
        debug_value("EI_CLASS", EI.CLASS, info="32-bit" if EI.CLASS == b"\x01" else "64-bit")
        debug_value("EI_DATA", EI.DATA, info=self.byteorder)
        debug_value("EI_VERSION", EI.VERSION)
        
        self.read(9) # PADDING
        
        e.type = self.read(2)
        e.machine = self.read(2)
        e.version = self.read(4)
        e.entry = self.read(8)
        e.phoff = self.read(8)
        e.shoff = self.read(8)
        
        self.read(4) # PADDING
        
        e.ehsize = self.read(2)
        e.phentsize = self.read(2)
        e.phnum = self.read(2)
        e.shentsize = self.read(2)
        e.shnum = self.read(2)
        e.shstrndx = self.read(2)
        
        debug(" # E HEADER")
        
        debug_value("e_type", e.type)
        debug_value("e_machine", e.machine)
        debug_value("e_version", e.version)
        debug_value("e_entry", e.entry)
        debug_value("e_phoff", e.phoff)
        debug_value("e_shoff", e.shoff)
        debug_value("e_ehsize", e.ehsize)
        debug_value("e_phentsize", e.phentsize)
        debug_value("e_phnum", e.phnum)
        debug_value("e_shentsize", e.shentsize)
        debug_value("e_shnum", e.shnum)
        debug_value("e_shstrndx", e.shstrndx)
        
        #
        #   Program Header Table
        #
        
        self.f.seek(e.phoff)
        
        p.type = self.read(4)
        p.flags = self.read(4)
        p.offset = self.read(8)
        p.vaddr = self.read(8)
        p.paddr = self.read(8)
        p.filesz = self.read(8)
        p.memsz = self.read(8)
        
        debug(" # P HEADER")
        
        debug_value("p_type", p.type)
        debug_value("p_flags", p.flags)
        debug_value("p_offset", p.offset)
        debug_value("p_vaddr", p.vaddr)
        debug_value("p_paddr", p.paddr)
        debug_value("p_filesz", p.filesz)
        debug_value("p_memsz", p.memsz)
        
        #
        #   Section Header Table
        #
        
        for i in range(e.shnum):
            self.f.seek(e.shoff + i * e.shentsize)
            
            h = sh()
            h.name = self.read(4)
            h.type = self.read(4)
            h.flags = self.read(8)
            h.addr = self.read(8)
            h.offset = self.read(8)
            h.size = self.read(8)
            
            self.read(24) # PADDING
    
        name_section = sh.all[e.shstrndx]
        
        for h in sh.all:
            self.f.seek(name_section.offset + h.name)
            
            name = ""
            while (byte := self.read(1)) != 0x0:
                name += chr(byte)
        
            debug(f" # {name} SECTION HEADER")
            
            debug_value("sh_name", h.name)
            debug_value("sh_type", h.type)
            debug_value("sh_flags", h.flags)
            debug_value("sh_addr", h.addr)
            debug_value("sh_offset", h.offset)
            debug_value("sh_size", h.size)
                
            sh.names.append(name)
    
        for i, name in enumerate(sh.names):
            if name == ".text" and e.entry == sh.all[i].addr:
                code_offset = sh.all[i].offset
                break
        else:
            code_offset = e.entry - p.paddr
            
            for i, name in enumerate(sh.names):
                if name == ".symtab":
                    symtab_offset = sh.all[i].offset
                    symtab_size = sh.all[i].size
                elif name == ".strtab":
                    strtab_offset = sh.all[i].offset
                
            self.f.seek(symtab_offset)
            
            for i in range(symtab_size // 24):
                st_name = self.read(4)
                st_info = self.read(1)
                st_other = self.read(1)
                st_shndx = self.read(2)
                st_value = self.read(8)
                st_size = self.read(8)
                
                debug_value("st_name", st_name)
                debug_value("st_info", st_info)
                debug_value("st_other", st_other)
                debug_value("st_shndx", st_shndx)
                debug_value("st_value", st_value)
                debug_value("st_size", st_size)
                
                # Useless at the moment
                # tell = self.f.tell()
                # self.f.seek(strtab_offset + st_name)
                
                # name = ""
                # while (byte := self.read(1)) != 0x0:
                #     name += chr(byte)
                    
                # self.f.seek(tell)
        
        self.f.seek(code_offset)
        
        debug(" ! SANDBOX")
        
        sandbox = Sandbox(self.f, code_offset, self.byteorder)
        sandbox.execute()