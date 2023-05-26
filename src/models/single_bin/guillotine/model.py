from __future__ import annotations
import itertools


import math
import time
import numpy as np

from src.models.abstract_model import AbstractSingleBinModel, constraint
from src.data_structures.bin import Bin
from src.data_structures.machine_config import MachineConfig
from ..anchor.single_bin_packing import SingleBinPacking

from cpmpy import Model, AllEqual
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import all, any
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.variables import intvar, boolvar, NDVarArray, cpm_array, _IntVarImpl, _genname
from cpmpy.expressions.globalconstraints import Element, Xor

from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from ..anchor.item_packing import ItemPacking


class GuillotineSBM(AbstractSingleBinModel):

    def __init__(self, 
                    machine_config: MachineConfig, 
                    single_bin_packing: SingleBinPacking,
                    is_end_packing: bool = False
                ):

        # Save the provided arguments as attributes
        self.machine_config = machine_config
        self.single_bin_packing = single_bin_packing
        self.is_end_packing = is_end_packing

        # Will at the end containt all constraints for later retrieval
        self.constraints = []

        self.stats = {}

        self.init_variables()
        self.model = Model()
        self.cpm_vars = []
        self.vals = []

    @classmethod
    def init_from_problem(cls, problem) -> GuillotineSBM:
        sbp = SingleBinPacking(
                _items=problem.get_item_packing(ItemPacking),
                _items_rotated=problem.get_item_packing_rotated(ItemPacking),
                bin=Bin(config=problem.get_bin_config()),
            )
        return cls(
            problem.get_machine_config(),
            sbp,
            True
        )
    
    def get_name():
        return "Guillotine"

    def init_variables(self):
        self.bin_length = self.machine_config.max_length #intvar(self.machine_config.min_length, self.machine_config.max_length) # the bin length
        self.bin_width = self.machine_config.width # the bin width
        self.items = self.single_bin_packing.items
        self.widths = sorted(set([item.width for item in self.items]))
        self.heights = [item.height for item in self.items]

        self.P = self.bin_length // min(self.heights) # upper limit on number of cutting patterns
        self.Pmin = min(self.widths) # minimum length of cutting pattern
        self.Pmax = self.bin_length # maximum length of cutting pattern

        self.A = self.bin_width // min(self.widths) # upper bound on number of strips
        self.B = self.Pmax // min(self.heights) # upper bound on number of vertical cuts

        
        self.W = len(self.widths) # number of unique widths
        self.I = len(self.items) # number of items to pack

        self.beta = boolvar(self.P) # if the pth cutting pattern exists (is used)
        self.pattern_length = intvar(0,self.Pmax,self.P) # the length of the pth pattern 
        self.gamma = boolvar((self.P,self.A,self.W)) # if the ath strip of the pth cutting pattern producs a piece of the wth width
        self.sigma = boolvar((self.P,self.A,self.B,self.I)) # if the bth cut of the ath strip of the pth pattern produces the ith item type

    def get_constraints_per_type(self):
        return {
            "constraints" : self.get_constraints(),
        }
    
    @constraint
    def get_constraints(self):
        
        c = []

        # 1.1
        # -> definition of bin length lower bound

        # 1.2
        # -> definition of bin length upper bound

        # 1.3
        for (beta1,beta2) in itertools.pairwise(self.beta):
            c.append(beta1 >= beta2)

        # 1.4
        # -> definition pattern length lower bound
        for p in range(self.P):
            # c.append(self.beta[p].implies(self.pattern_length[p] >= self.Pmin)) # ✅
            # c.append((~self.beta[p]).implies(self.pattern_length[p] == 0)) # ✅
            c.append(self.pattern_length[p] >= self.Pmin*self.beta[p])

        # 1.5
        # -> definition pattern length upper bound
        for p in range(self.P):
            c.append(self.pattern_length[p] <= self.Pmax*self.beta[p])

        # 1.6
        # -> the sum of all pattern lengths must not exceed the bin length
        c.append(cpm_sum(self.pattern_length) <= self.bin_length)

        # 1.7 - 1.8
        for p in range(self.P):
            for a in range(self.A-1):
                # 1.7
                c.append(cpm_sum(self.gamma[p,a+1,:]) <= cpm_sum(self.gamma[p,a,:]))
                #c.append((cpm_sum(self.gamma[p,a+1,:]) != 0).implies(cpm_sum(self.gamma[p,a,:]) != 0)) # ✅

            for a in range(self.A):
                # 1.8
                c.append(cpm_sum(self.gamma[p,a,:]) <= 1) # ✅

            # 1.9    
            # -> a pattern can only exist if its first strip has a width    
            c.append(cpm_sum(self.gamma[p,0,:]) >= self.beta[p])
            #c.append(self.beta[p].implies(sum(self.gamma[p,0,:]) != 0 ))
            # print("TEST", cpm_sum(self.gamma[p,0,:]) > 0)

            # 1.10
            #c.append(cpm_sum(self.gamma[p,:,:]*np.array([self.widths]).T) <= self.bin_width)
            c.append(cpm_sum([cpm_sum(self.gamma[p,:,w])*self.widths[w] for w in range(self.W)]) <= self.bin_width)


        # 1.11
        for p in range(self.P):
            for a in range(self.A):
                for b in range(self.B-1):
                    # 1.11
                    c.append(cpm_sum(self.sigma[p,a,b+1,:]) <= cpm_sum(self.sigma[p,a,b,:]))
                    #c.append((cpm_sum(self.sigma[p,a,b+1,:]) != 0).implies(cpm_sum(self.sigma[p,a,b,:])!=0))


        for p in range(self.P):
            for a in range(self.A):

                c.append((cpm_sum(self.gamma[p,a,:]) != 0).implies(cpm_sum(self.sigma[p,a,0,:]) != 0)) # ✅

                for b in range(self.B):   
                    # 1.12
                    c.append(cpm_sum(self.sigma[p,a,b,:]) <= 1) # ✅

                    # 1.13
                    for w in range(self.W):
                        c.append(
                            cpm_sum(
                                [self.sigma[p,a,b,i] for i in range(self.I) if self.items[i].width == self.widths[w]]
                            ) <= self.gamma[p,a,w]
                            )

                # 1.14
                # -> thus sum of the heights of all items in strip must be at most the length of the pattern
                c.append(cpm_sum([cpm_sum(self.sigma[p,a,:,i])*self.heights[i] for i in range(self.I)]) <= self.pattern_length[p])

        # 1.15
        # for i in range(self.I):
        #     c.append(cpm_sum(self.sigma[:,:,:,i]) >= 1)
        # -> min production

        # 1.16
        # -> max production

        # 1.17 - 1.22
        # -> variable domains

        # S1
        for p in range(self.P-1):
            c.append(self.pattern_length[p] >= self.pattern_length[p+1])

        # S2
            for a in range(self.A-1):
                for w in range(self.W):
                    c.append(cpm_sum([self.gamma[p,a,w_] for w_ in range(w,self.W)]) >= self.gamma[p,a+1,w])

        # S3
            for a in range(self.A):
                for b in range(self.B-1):
                    for i in range(self.I):
                        c.append(cpm_sum([self.sigma[p,a,b,i_] for i_ in range(i,self.I)]) >= self.sigma[p,a,b,i])


        for i,count in enumerate(self.single_bin_packing.counts):
            c.append(count == cpm_sum(self.sigma[:,:,:,i]) + cpm_sum(self.sigma[:,:,:,i+self.I//2]))
        c.append(self.single_bin_packing.bin.length == self.bin_length)

        self.constraints.extend(c)

        return c


    def get_objective(self):

        # Waste
        o1 = self.bin_width*self.bin_length - cpm_sum([cpm_sum(self.sigma[:,:,:,i])*self.items[i].item.area for i in range(self.I)])

        o = o1

        return o
    
    def get_variables(self):
        return self.beta.tolist() + self.pattern_length.tolist() + self.gamma.flatten().tolist() + self.sigma.flatten().tolist()
    
    def solve(self, max_time_in_seconds=1):

        self.c = self.get_constraints()
        self.stats["nr_constraints"] = len(self.c)
        self.model += self.c

        self.o = self.get_objective()
        self.model.minimize(self.o)

        print("Transferring...")
        start_t = time.perf_counter()
        s = CPM_ortools(self.model)
        s.solution_hint(self.cpm_vars, self.vals)
        end_t = time.perf_counter()
        self.stats["transfer_time"] = end_t - start_t

        print("Solving...")
        start_s = time.perf_counter()
        res = s.solve( max_time_in_seconds=max_time_in_seconds)
        end_s = time.perf_counter()
        self.stats["solve_time"] = end_s - start_s

        return res
    
    def fix(self):
        self.single_bin_packing.fix()

    def get_stats(self):

        self.stats["density"] = float(np.sum([np.sum(self.sigma[:,:,:,i]).value()*self.items[i].item.area for i in range(self.I)]) / (self.bin_length*self.bin_width))
        self.stats["bin_length"] = int(self.bin_length)
        self.stats["fulfilled"] = np.array([np.sum(self.sigma.value()[:,:,:,i]) + np.sum(self.sigma.value()[:,:,:,i+self.I//2]) for i in range(self.I//2)]).astype(int).tolist()
        self.stats["counts"] = np.array(self.single_bin_packing.counts).astype(int).tolist()

        self.stats["objective"] = int(self.o.value())
        self.stats["nr_variables"] = len(self.get_variables())
        #self.stats["ortools_nr_constraints"] = len(self.model.constraints)
        self.stats["ortools_objective"] = int(self.model.objective_value())

        return self.stats


    def visualise(self):
        np.random.seed(seed=42)

        bin_width = self.bin_width
        bin_height = self.machine_config.max_length

        #bin_height /= bin_width
            
        fig_size = (10*bin_height/bin_width,10)
        (fig, ax) = plt.subplots(figsize=fig_size)

        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_visible(False)
        
        ax.set_xlim((0, 1))
        ax.set_ylim((0, 1))

        cmap = get_cmap(self.I//2)



        pattern_height = 0
        for p in range(self.P):
            strip_width = 0
            for a in range(self.A):
                cut_height = 0
                max_width = 0
                for b in range(self.B):
                    for i in range(self.I):
                        if (self.sigma[p,a,b,i].value()):


                            ax.add_patch(
                                plt.Rectangle(
                                    (
                                        (pattern_height+cut_height)/bin_height,
                                        strip_width/bin_width
                                    ),
                                    self.items[i].height/bin_height,
                                    self.items[i].width/bin_width,
                                    edgecolor='black',
                                    facecolor=cmap(i%(self.I//2)),
                                    #alpha=0.5
                                )
                            )
                            
                            max_width = max((max_width, self.items[i].width))
                        
                            cut_height += self.items[i].height
                            break

                strip_width += sum(self.gamma[p,a,:].value()*self.widths) #max_width

            pattern_height += self.pattern_length[p].value()
      
        
    

 

    
def get_cmap(n, name='tab20'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
