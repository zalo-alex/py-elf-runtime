# Py ELF Sandbox

A Python ELF x86-64 Sandbox, it parse, decompile on the fly and executes it in a Sandbox
> (The sandbox has direct access to your operating system, the aim is not to create an isolated VM.)

## Basic Usage

Using a test sample:

```bash
$ python3 main.py tests/working/simple64/simple64.elf
Hello World!
```

## Debug Mode

Add `debug` in the command to see all headers, register and other debug infos
```bash
$ python3 main.py tests/working/simple64/simple64.elf
...
# E HEADER
    e_type: 0x2
    e_machine: 0x3e
    e_version: 0x1
    e_entry: 0x10000080
    e_phoff: 0x40
    e_shoff: 0xf0
    e_ehsize: 0x40
    e_phentsize: 0x38
    e_phnum: 0x1
    e_shentsize: 0x40
    e_shnum: 0x4
    e_shstrndx: 0x3
...
# .text SECTION HEADER
    sh_name: 0xb
    sh_type: 0x1
    sh_flags: 0x6
    sh_addr: 0x10000080
    sh_offset: 0x80
    sh_size: 0x31
...
```

## Supported Instructions

> See `src/sandbox.py` for the exact list  
> Ref: https://ref.x86asm.net/coder64.html

#### MOV
`b8+r`, `c7`

#### XOR
`31`

#### SYSCALL
`05`

## Ignored Instructions

#### ENDBR64
`f30f1efa`

## Supported Syscalls

```
0x1: write
0x3c: exit
```

## References:
https://code.google.com/archive/p/corkami/wikis/ELF101.wiki  
https://ref.x86asm.net/coder64.html