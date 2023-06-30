from __future__ import annotations
from abc import ABCMeta, abstractmethod


from contextlib import contextmanager
from timeit import default_timer as timer
import threading
import _thread


from cpmpy.solvers import CPM_ortools 
from cpmpy import Model

from src.data_structures.abstract_item_packing import AbstractItemPacking
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking
from src.data_structures.machine_config import MachineConfig
from src.data_structures.abstract_single_bin_packing import AbstractSingleBinPacking

from src.utils.configuration import Configuration

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
        raise TimeoutException("Timed out for operation \"{}\"".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


class Alarm():

    def __init__(self, config:Configuration):
        self.config = config

        if config.linux:
            import signal
            self.signal = signal.signal(signal.SIGALRM, handler)

    def start(self, timeout):
        if self.config.linux:
            self.signal.alarm(timeout)
        else:
            print("Warning, timeout protection only supported on Linux!")

    def cancel(self):
        if self.config.linux:
            self.signal.alarm(0)
        else:
            pass

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

    def solve(self, config:Configuration, max_time_in_seconds=1, constraint_creation_timeout=60*3, constraint_transfer_timeout=60*2):

        alarm = Alarm(config=config)
        
        self.sat = False

        try:
            print("Collecting constraints ...")
            with time_limit(constraint_creation_timeout, 'creation'):
                alarm.start(constraint_creation_timeout) 
                self.c = self.get_constraints()
                self.stats["nr_constraints"] = len(self.c)
                print("nr constraints:", len(self.c))
                alarm.cancel()

            self.o = self.get_objective()
            self.objective += self.o

            self.model += self.constraints
            self.model.minimize(self.objective)

            print("Transferring...")
            with time_limit(constraint_transfer_timeout, 'transfer'):
                start_t = timer()
                alarm.start(constraint_transfer_timeout) 
                s = CPM_ortools(self.model)
                alarm.cancel()
                end_t = timer()
                self.stats["transfer_time"] = end_t - start_t

            print("Solving...")
            start_s = timer()
            res = s.solve( max_time_in_seconds=max_time_in_seconds)
            end_s = timer()
            self.stats["solve_time"] = end_s - start_s
        except TimeoutException as e: 
            print(e)
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


    # Constructor
    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: AbstractSingleBinPacking
                ):

        # Save the provided arguments as attributes
        self.machine_config = machine_config
        self.single_bin_packing = single_bin_packing

        # CPMpy model data
        self.constraints = []
        self.objective = 0
        self.model = Model()

        # To collect data about the algorithm
        self.stats = {}

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
        # return [ 
        #     self.single_bin_packing.bin.config.max_length == self.single_bin_packing.bin.length,
        #     ]
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

