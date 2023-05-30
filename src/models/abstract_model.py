from __future__ import annotations
from abc import ABCMeta, abstractmethod

#import signal
from contextlib import contextmanager
from timeit import default_timer as timer
import threading
import _thread


from cpmpy.solvers import CPM_ortools 

from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

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

def handler(signum, frame):
    print("Forever is over!")
    raise Exception("end of time")

try:
    signal.signal(signal.SIGALRM, handler)
except:
    pass

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


class Alarm():

    alarm = None

    def watchdog():
        print('Watchdog expired. Exiting...')
        raise Exception("end of time")

    def start(self, timeout):
        self.alarm = threading.Timer(timeout, Alarm.watchdog)
        self.alarm.start()

    def cancel(self):
        self.alarm.cancel()

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
    def get_constraints(self): pass

    @abstractmethod
    def get_objective(self): pass

    def solve(self, max_time_in_seconds=1, constraint_creation_timeout=60*2, constraint_transfer_timeout=60):

        alarm = Alarm()
        
        self.sat = False

        
        try:
            with time_limit(constraint_creation_timeout, 'creation'):
                #alarm.start(constraint_creation_timeout) 
                self.c = self.get_constraints()
                self.stats["nr_constraints"] = len(self.c)
                #alarm.cancel()

            self.o = self.get_objective()
            self.objective += self.o

            self.model += self.constraints
            self.model.minimize(self.objective)

            print("Transferring...")
            with time_limit(constraint_transfer_timeout, 'transfer'):
                start_t = timer()
                #alarm.start(constraint_transfer_timeout) 
                s = CPM_ortools(self.model)
                #alarm.cancel()
                end_t = timer()
                self.stats["transfer_time"] = end_t - start_t

            print("Solving...")
            start_s = timer()
            res = s.solve( max_time_in_seconds=max_time_in_seconds)
            end_s = timer()
            self.stats["solve_time"] = end_s - start_s
        except: 
            return False

        # Fix the solution to bound variables
        if res:
            self.sat = True
            self.single_bin_packing.fix()

        return res

    #@abstractmethod
    def get_repeats(self): pass

    @abstractmethod
    def get_stats(self): pass

    @abstractmethod
    def fix(self): pass

class AbstractSingleBinModel(AbstractModel):

    def __init__(self, ItemPacking:AbstractItemPacking, SingleBinPacking:AbstractSingleBinPacking):
        self.ItemPacking = ItemPacking
        self.SingleBinPacking = SingleBinPacking

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
    def bin_length(self):
        # The bin length should be at least its minimal value
        return [ 
            self.single_bin_packing.bin.config.min_length <= self.single_bin_packing.bin.length,
            self.single_bin_packing.bin.length <= self.single_bin_packing.bin.config.max_length 
            ]




class AbstractMultiBinModel(AbstractModel):

    def __init__(self):
        pass

class AbstractProductionModel(AbstractModel):

    def __init__(self):
        pass

