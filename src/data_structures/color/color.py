from dataclasses import dataclass

@dataclass()
class Color:

    r: float
    g: float
    b: float

    @property
    def tuple(self) -> tuple[float]:
        return (self.r, self.g, self.b)
    
    def visualise(self):
        return self.tuple

    @property
    def hex(self) -> str:
        return '#{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b)

    def __hash__(self):
        return hash(self.tuple)

    def __eq__(self, other):
        if isinstance(other, Color):
            return (self.r == other.r) & (self.g == other.g) & (self.b == other.b)
        else:
            return False

RED = Color(1,0,0)
GREEN = Color(0,1,0)
BLUE = Color(0,0,1)
PURPLE = Color(1,0,1)
CYAN = Color(0,1,1)