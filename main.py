from src.parser import Parser

import sys

Parser("./tests/working/simple64/simple64.elf" if len(sys.argv) < 2 else sys.argv[1]).parse()