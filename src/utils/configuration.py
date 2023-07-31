from dataclasses import dataclass

import sys

@dataclass
class Configuration:

    @property
    def linux(self): return sys.platform == "linux"

    @property
    def windows(self): return sys.platform == "windows"

    @property
    def mac(self): return sys.platform == "mac"
