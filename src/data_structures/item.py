from dataclasses import dataclass

@dataclass(kw_only=True)
class Item():

    ID: int
    width: int
    height: int
    may_rotate: bool = True

        
    @property
    def area(self) -> int:
        return self.width*self.height   

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.ID == other.ID
        else:
            return False


