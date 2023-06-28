import numpy as np
import uuid
from tqdm import tqdm_notebook as tqdm

from cpmpy import *
from cpmpy.solvers import CPM_ortools 
from cpmpy.expressions.python_builtins import all as cpm_all
from cpmpy.expressions.python_builtins import any as cpm_any
from cpmpy.expressions.python_builtins import sum as cpm_sum
from cpmpy.expressions.python_builtins import max as cpm_max

def generate():
    
    np.random.seed(42)

    machine_width = 40
    machine_length_range = [40, 250]
    item_width_range = [10, machine_width]
    item_height_range = [10, 40]
    nr_items_range = [1, 5]

    nr_deadlines_range = [1, 5]
    deadline_range = [0, 500]
    counts_range = [50, 500]

    machine_lengths = np.random.random_integers(machine_length_range[0], machine_length_range[1], 10)
    widthss = np.random.random_integers(item_width_range[0], item_width_range[1], 10)
    heightss = np.random.random_integers(item_height_range[0], item_height_range[1], 10)
    nr_itemss = np.random.random_integers(nr_items_range[0], nr_items_range[1], 10)


    bench_list = {}

    machine_lengths = np.arange(40, 100, 20)
    nr_itemss = [5, 10, 15]

    for machine_length in machine_lengths:
        for nr_items in nr_itemss:
            widths = np.random.choice(widthss, size=nr_items, replace=False)
            heights = np.random.choice(heightss, size=nr_items, replace=False)
            nr_deadlines = np.random.choice(np.arange(nr_deadlines_range[0], nr_deadlines_range[1]))
            deadlines = sorted([int(np.random.choice(np.arange(deadline_range[0], deadline_range[1]))) for _ in range(nr_deadlines)])

            deadline_counts = []

            for i_item in range(nr_items):
                counts = []
                for i_deadline in range(nr_deadlines):
                    b = np.random.choice([0,1])
                    c = np.random.choice(np.arange(counts_range[0], counts_range[1]))
                    counts.append(int(b*c))
                deadline_counts.append(counts)


                
   
            bench = {
                "widths": [int(w) for w in widths.tolist()],
                "heights": [int(h) for h in heights.tolist()],
                "deadlines": deadlines,
                "deadline_counts": deadline_counts,
                "machine_config": {
                    "width": int(machine_width),
                    "min_length": int(machine_length),
                    "max_length": int(machine_length)
                }
                }
            bench_list[str(uuid.uuid4())] = bench

    return bench_list

def generate_deterministic():
    np.random.seed(42)

    machine_width = 40
    item_width_range = [10, machine_width]
    item_height_range = [10, 40]
    nr_items_range = [1, 5]

    nr_deadlines_range = [1, 5]
    deadline_range = [0, 500]
    counts_range = [20, 500]

    machine_lengths = np.arange(250, 250+1, 40)
    nr_itemss = np.arange(1,10+1,3)
    nr_deadliness = np.arange(1,5+1,1)

    nr_creelss = np.arange(1,1+5,1)




    bench_list = {}

    for machine_length in tqdm(machine_lengths, desc="machine length", leave=True):
        for nr_deadlines in tqdm(nr_deadliness, desc="nr deadlines", leave=False):
            for nr_items in tqdm(nr_itemss, desc="nr items", leave=False):
                for nr_creel in nr_creelss:
                    for nr_creel_colors in range(nr_items):


                        widths = np.random.random_integers(item_width_range[0], item_width_range[1], nr_items)
                        heights = np.random.random_integers(item_height_range[0], item_height_range[1], nr_items)
                        deadlines = sorted(np.random.random_integers(deadline_range[0], deadline_range[1], nr_deadlines))

                        model = Model()

                        item_counts = intvar(0, 500, (nr_items, nr_deadlines))

                        c = []

                        # The total (relaxed) area of the demand can not exceed the capacity
                        for i_deadline in range(nr_deadlines):
                            capacity_percentage = 1#(np.random.random() + 4) / 5
                            c.append( cpm_sum([cpm_sum(item_counts[i_item,:i_deadline+1])*widths[i_item]*heights[i_item] for i_item in range(nr_items)]) <= (deadlines[i_deadline]+1)*int(machine_length*machine_width*capacity_percentage) )

                        # A deadline should have some demand
                        for i_deadline in range(nr_deadlines):
                            c.append( cpm_sum(item_counts[:,i_deadline]) > 0 )

                        # An item should have some demand
                        for i_item in range(nr_items):
                            c.append( cpm_sum(item_counts[i_item,:]) > 0 )

                        item_counts_hint = np.random.random_integers(counts_range[0], counts_range[1], (nr_items, nr_deadlines))

                        model += c
                        model.minimize(cpm_sum([(item_counts_hint[i_item, i_deadline] - item_counts[i_item, i_deadline])**2 for i_item in range(nr_items) for i_deadline in range(nr_deadlines)]))

                        s = CPM_ortools(model)

                        
                        s.solution_hint(item_counts.flatten().tolist(), item_counts_hint.flatten().tolist())

                        s.solve(10)

                        deadline_counts = item_counts.value().astype(int).tolist()

                        bench = {
                            "widths": [int(w) for w in widths.tolist()],
                            "heights": [int(h) for h in heights.tolist()],
                            "deadlines": [int(d) for d in deadlines],
                            "deadline_counts": deadline_counts,
                            "colors": [i for i in range(nr_items)], # elk item een unieke kleur geven, anders niet deterministisch genoege benchmark
                            "machine_config": {
                                "width": int(machine_width),
                                "min_length": int(machine_length),
                                "max_length": int(machine_length),
                                "max_creel_number": int(nr_creel),
                                "max_creel_colors": int(nr_creel_colors)+1,
                                "creel_switch_penalty": 10
                            }
                            }
                        bench_list[str(uuid.uuid4())] = bench


    return bench_list

def generate_small():
    np.random.seed(42)

    machine_width = 40
    item_width_range = [10, machine_width]
    item_height_range = [10, 40]
    nr_items_range = [1, 5]

    nr_deadlines_range = [1, 5]
    deadline_range = [0, 500]
    counts_range = [20, 500]




    machine_lengths = [250] #np.arange(450, 900, 15)
    nr_deadliness = [1,3,5] #np.arange(1,5+1,1)
    nr_itemss = [5] # [5,10]
    
    
    nr_creelss = [5] #np.arange(1,1+5,1)
    nr_creel_colorss = [3]

    nr_instances = 5

    bench_list = {}

    for machine_length in tqdm(machine_lengths, desc="machine length", leave=True):
        for nr_deadlines in tqdm(nr_deadliness, desc="nr deadlines", leave=False):
            for nr_items in tqdm(nr_itemss, desc="nr items", leave=False):
                for nr_creel in nr_creelss:
                    for nr_creel_colors in nr_creel_colorss:
                        if nr_creel_colors > nr_items:
                            continue

                        widths = np.random.random_integers(item_width_range[0], item_width_range[1], nr_items)
                        heights = np.random.random_integers(item_height_range[0], item_height_range[1], nr_items)
                        deadlines = sorted(np.random.random_integers(deadline_range[0], deadline_range[1], nr_deadlines))

                        model = Model()

                        item_counts = intvar(0, 500, (nr_items, nr_deadlines))

                        c = []

                        # The total (relaxed) area of the demand can not exceed the capacity
                        for i_deadline in range(nr_deadlines):
                            capacity_percentage = 1#(np.random.random() + 4) / 5
                            c.append( cpm_sum([cpm_sum(item_counts[i_item,:i_deadline+1])*widths[i_item]*heights[i_item] for i_item in range(nr_items)]) <= (deadlines[i_deadline]+1)*int(machine_length*machine_width*capacity_percentage) )

                        # A deadline should have some demand
                        for i_deadline in range(nr_deadlines):
                            c.append( cpm_sum(item_counts[:,i_deadline]) > 0 )

                        # An item should have some demand
                        for i_item in range(nr_items):
                            c.append( cpm_sum(item_counts[i_item,:]) > 0 )

                        item_counts_hint = np.random.random_integers(counts_range[0], counts_range[1], (nr_items, nr_deadlines))

                        model += c
                        model.minimize(cpm_sum([(item_counts_hint[i_item, i_deadline] - item_counts[i_item, i_deadline])**2 for i_item in range(nr_items) for i_deadline in range(nr_deadlines)]))

                        s = CPM_ortools(model)

                        
                        s.solution_hint(item_counts.flatten().tolist(), item_counts_hint.flatten().tolist())

                        s.solve(10)

                        deadline_counts = item_counts.value().astype(int).tolist()

                        bench = {
                            "widths": [int(w) for w in widths.tolist()],
                            "heights": [int(h) for h in heights.tolist()],
                            "deadlines": [int(d) for d in deadlines],
                            "deadline_counts": deadline_counts,
                            "colors": [i for i in range(nr_items)], # elk item een unieke kleur geven, anders niet deterministisch genoege benchmark
                            "machine_config": {
                                "width": int(machine_width),
                                "min_length": int(machine_length),
                                "max_length": int(machine_length),
                                "max_creel_number": int(nr_creel),
                                "max_creel_colors": int(nr_creel_colors),
                                "creel_switch_penalty": 10
                            }
                            }
                        
                        name = str(nr_deadlines) + "_" + str(nr_items) + "_" + str(nr_creel_colors)
                        #bench_list[str(uuid.uuid4())] = bench
                        bench_list[name] = bench


    return bench_list