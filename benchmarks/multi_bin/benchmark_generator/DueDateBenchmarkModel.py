
import numpy as np

from cpmpy import *
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import sum as cpm_sum


class DueDateBenchmarkModel():

    '''
    CPMpy model for generating realistic problem instances.
    '''

    def __init__(self,
                    nr_items: int,
                    nr_deadlines: int,
                    item_widths: list[int],
                    item_heights: list[int],
                    object_width: int,
                    object_length: int,
                ):
        self.nr_items = nr_items
        self.nr_deadlines = nr_deadlines

        self.item_widths = item_widths
        self.item_heights = item_heights

        self.object_width = object_width
        self.object_length = object_length

        self.demand_lower = 0
        self.demand_upper = 1000

        self.demand_hint_lower = 20
        self.demand_hint_upper = 500

        self.deadline_interval_lower = 2
        self.deadline_interval_upper = 500

        self.deadline_lower = 0
        self.deadline_upper = 500

    def create_variables(self):
        
        self.item_demand = intvar(self.demand_lower, self.demand_upper, (self.nr_items, self.nr_deadlines))
        self.deadline_interval = intvar(self.deadline_interval_lower, self.deadline_interval_upper, (self.nr_deadlines))

        # Auxilary variable
        self.deadline_time = cpm_array(np.cumsum(self.deadline_interval))

    def create_solution_hints(self):

        self.item_demand_hint = np.random.random_integers(self.demand_hint_lower, self.demand_hint_upper, (self.nr_items, self.nr_deadlines))
        self.deadline_time_hint = sorted(np.random.random_integers(self.deadline_lower, self.deadline_upper, self.nr_deadlines))

    def get_constraints(self):
        
        c = []

        # 1) The total (relaxed) area of the demand can not exceed the capacity
        for i_deadline in range(self.nr_deadlines):
            c.append( 
                cpm_sum([
                    cpm_sum(self.item_demand[i_item,:i_deadline+1])*self.item_widths[i_item]*self.item_heights[i_item] for i_item in range(self.nr_items)
                ]) 
                <= 
                (self.deadline_time[i_deadline]+1)*int(self.object_length*self.object_width) 
                )

        # 2) A deadline should have some demand
        for i_deadline in range(self.nr_deadlines):
            c.append( cpm_sum(self.item_demand[:,i_deadline]) > 0 )

        # 3) An item should have some demand
        for i_item in range(self.nr_items):
            c.append( cpm_sum(self.item_demand[i_item,:]) > 0 )

        # 4) The deadlines should fall within the specified time range
        for i_deadline in range(self.nr_deadlines):
            c.append( self.deadline_time[0] >= self.deadline_lower )
            c.append( self.deadline_time[-1] <= self.deadline_upper )

        return c
    
    def get_objective(self):

        o1 = cpm_sum( ((self.item_demand_hint - self.item_demand)**2).flatten() )

        o2 = cpm_sum( ((self.deadline_time_hint - self.deadline_time)**2).flatten() )

        # Lexicographical linearisation of objectives
        o = o2*100000 + o1

        return o

    def solve(self, timeout=10):
        self.create_variables()
        self.create_solution_hints()

        self.model = Model()

        self.model += self.get_constraints()
        self.model.minimize(self.get_objective())

        s = CPM_ortools(self.model)
  
        s.solution_hint(
            self.item_demand.flatten().tolist(), #+ self.deadline_time.tolist(), 
            self.item_demand_hint.flatten().tolist() #+ self.deadline_time_hint
            )

        sat = s.solve(timeout)

        return sat
    
    def export(self) -> str:

        bench = {
                    "widths": [int(w) for w in self.item_widths],
                    "heights": [int(h) for h in self.item_heights],
                    "deadlines": [int(d) for d in self.deadline_time.value().astype(int).tolist()],
                    "deadline_counts": self.item_demand.value().astype(int).tolist(),
                    "machine_config": {
                        "width": int(self.object_width),
                        "min_length": int(self.object_length),
                        "max_length": int(self.object_length)
                    }
                }
        
        return bench