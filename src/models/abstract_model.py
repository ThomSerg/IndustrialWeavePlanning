from __future__ import annotations
from abc import ABCMeta, abstractmethod

from timeit import default_timer as timer

def constraint(func):
        def count_constraints(self):
            # g = func.__globals__
            # sentinel = object()

            # oldvalue = g.get('c', sentinel)
            # g['c'] = []

            # try:
            #     start = timer()
            #     func(self)
            #     end = timer()
            #     c = g.get('c')
            #     self.constraints_stats[func.__name__] = { 
            #         "nr_constraint": len(c),
            #         "creation_time": end-start
            #     }
            # except:
            #     g['c'] = oldvalue

            start = timer()
            c = func(self)
            end = timer()
            self.constraints_stats[func.__name__] = { 
                "nr_constraint": len(c),
                "creation_time": end-start
            }

            return c
        return count_constraints

class AbstractModel(metaclass=ABCMeta):

    constraints_stats = {}

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def init_from_problem(cls, problem) -> AbstractModel: pass

    @abstractmethod
    def get_name(self): pass

    @abstractmethod
    def get_variables(self): pass

    @abstractmethod
    def get_constraints_per_type(self): pass

    @abstractmethod
    def get_constraints(self): pass

    @abstractmethod
    def get_objective(self): pass

    @abstractmethod
    def solve(self, timeout: int): pass

    #@abstractmethod
    def get_repeats(self): pass

    @abstractmethod
    def get_stats(self): pass

    @abstractmethod
    def fix(self): pass

class AbstractSingleBinModel(AbstractModel):

    def __init__(self):
        pass

    @constraint
    def item_count(self):
        # Link the item count variable with the number of active item instances
        return [ (item.count == sum(item.active)) for item in self.single_bin_packing.items]
    
    @constraint
    def item_selection(self):
        # If an item is active, it should be packed at least once
        # If an item is inactive, it should not be packed
        return [ ( item.selected == (item.count != 0) ) for item in self.single_bin_packing.items]
    
    @constraint
    def bin_height(self):
        # The bin length should be at least its minimal value
        return [ self.single_bin_packing.bin.length == self.single_bin_packing.bin.config.max_length ]




class AbstractMultiBinModel(AbstractModel):

    def __init__(self):
        pass
