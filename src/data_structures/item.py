from dataclasses import dataclass


@dataclass(kw_only=True)
class Item():

    '''
    An item.
    '''

    ID: int                     # identifier
    width: int                  # width
    height: int                 # length
    may_rotate: bool = True     # if rotation is allowed

    # Properties

    @property
    def area(self) -> int:
        return self.width*self.height   

    @property
    def smallest_side(self) -> int:
        return min((self.width, self.height))

    @property
    def largest_side(self) -> int:
        return max((self.width, self.height))
    
    # Equality comparison

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.ID == other.ID
        else:
            return False