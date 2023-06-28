from dataclasses import dataclass

import sys

@dataclass
class Configuration:

    @property
    def linux(self): return sys.platform == "Linux"

    @property
    def windows(self): return sys.platform == "Windows"

    @property
    def mac(self): return sys.platform == "Mac"
