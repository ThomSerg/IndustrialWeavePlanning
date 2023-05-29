import time
import pickle
import os
import json
import signal

import gc

import matplotlib.pyplot as plt

from src.data_structures.problem.problem import Problem
#from iterative.Visualiser import show_bin_packing
from src.data_structures.problem.multi_bin_problem import MultiBinProblem
from src.data_structures.problem.single_bin_problem import SingleBinProblem

from src.models.abstract_model import AbstractMultiBinModel, AbstractSingleBinModel
#from iterative.models.MultiBin.AbstractProductionModel import AbstractProductionModel
from src.extensions.due_dates.models.production_model import ProductionModel

import cpmpy


class BenchmarkSave():
    def __init__(
            self,
            problem: str,
            sat: bool,
            model
    ):
        self.problem = problem
        self.sat = sat
        self.model = model

def run_single_bin_benchmark(models: list[AbstractSingleBinModel], problems: list[SingleBinProblem], max_time_seconds=20):

    # problems.reverse()
    
    for problem in problems:
        print("PROBLEM", problem.name)
        print(problem.json_dict)
        for model in models:

            start = time.perf_counter()
            initialised_model = model.init_from_problem(problem)
            sat = initialised_model.solve(max_time_seconds)#60*4)
            end = time.perf_counter()

            bench_save = BenchmarkSave(str(problem.json_dict), sat, initialised_model)
            file_directory = os.path.join(os.getcwd(), model.get_name())
            file_name = os.path.join(file_directory, problem.name + ".pickle")

            if not os.path.exists(file_directory):
                os.makedirs(file_directory)

            with open(file_name, 'wb') as handle:
                pickle.dump(bench_save, handle, protocol=pickle.HIGHEST_PROTOCOL)

            print("SAT", sat)
            print("TIME", end-start)

            
            stats = initialised_model.get_stats()
            stats["total_time"] = end-start

            print("STATS", stats)
            file_name = os.path.join(file_directory, problem.name + ".json")
            with open(file_name, 'w') as handle:
                handle.write(json.dumps(stats, indent=4))

            if sat:
                #show_bin_packing(initialised_model.single_bin_packing)
                initialised_model.visualise()
                plt.savefig(os.path.join(file_directory, problem.name + '.png'))

                plt.show()
      

def run_single_bin_benchmark_repeated(models: list[AbstractSingleBinModel], problems: list[SingleBinProblem], start_index=0, max_time_seconds=20, nr_repeats=1):

    # problems.reverse()

    for problem in problems:
        print("PROBLEM", problem.name)
        print(problem.json_dict)
        for model in models:
            for i_repeat in range(nr_repeats):

                start = time.perf_counter()
                initialised_model = model.init_from_problem(problem)
                sat = initialised_model.solve(max_time_seconds)#60*4)
                end = time.perf_counter()

                bench_save = BenchmarkSave(str(problem.json_dict), sat, initialised_model)
                file_directory = os.path.join(os.getcwd(), "results", model.get_name())
                file_name = os.path.join(file_directory, problem.name + "_" + str(i_repeat) + ".pickle")

                if not os.path.exists(file_directory):
                    os.makedirs(file_directory)

                # with open(file_name, 'wb') as handle:
                #     pickle.dump(bench_save, handle, protocol=pickle.HIGHEST_PROTOCOL)

                print("SAT", sat)
                print("TIME", end-start)

                print(initialised_model.constraints_stats)

                if sat:
                    initialised_model.fix()
                    stats = initialised_model.get_stats()
                    stats["total_time"] = end-start

                    print("STATS", stats)
                    file_name = os.path.join(file_directory, problem.name + "_" + str(i_repeat) + ".json")
                    with open(file_name, 'w') as handle:
                        handle.write(json.dumps(stats, indent=4))

                    #show_bin_packing(initialised_model.single_bin_packing)
                    initialised_model.visualise()
                    plt.savefig(os.path.join(file_directory, problem.name + "_" + str(i_repeat) + '.png'))

                    plt.show()

def single_bin_benchmark_model_info(models: list[AbstractSingleBinModel], problems: list[SingleBinProblem], start_index=0, max_time_seconds=20, nr_repeats=1):

    # problems.reverse()

    model_complexity = []

    for problem in problems:
        print("PROBLEM", problem.name)
        print(problem.json_dict)
        for model in models:
            for i_repeat in range(nr_repeats):

                nr_constraints = {}

                initialised_model = model.init_from_problem(problem)

                c = initialised_model.get_constraints_per_type()

                for constraint_type in c.keys():
                    constraints = c[constraint_type]
                    l = [cpmpy.transformations.flatten_model.flatten_constraint(e) for e in constraints]
                    lf = flatten(l)
                    print(constraint_type + " : " + str(len(constraints)) + "->" + str(len(lf)))

                    nr_constraints[constraint_type] = len(lf)


                # l = [cpmpy.transformations.flatten_model.flatten_constraint(e) for e in c]
                # lf = flatten(l)

                print("------")
                # print(len(c))
                # print(len(lf))

                info = {}
                info["constraints"] = nr_constraints
                info["variables"] = len(initialised_model.get_variables())
                info["items"] = initialised_model.get_repeats()

                model_complexity.append(info)

                del initialised_model
                del c
                gc.collect()

    return model_complexity

def flatten(l):
    return [item for sublist in l for item in sublist]
   
def run_multi_bin_benchmark(
            solver_models: list[AbstractMultiBinModel], 
            production_models: list[ProductionModel],
            single_bin_models: list[AbstractSingleBinModel],
            problems: list[MultiBinProblem], 
            args: dict
        ):

    # problems.reverse()

    for problem in problems:
        print("PROBLEM", problem.name)
        print(problem.json_dict)
        for (solver_model, production_model, single_bin_model) in zip(solver_models, production_models, single_bin_models):

            start = time.perf_counter()
            initialised_model = solver_model.init_from_problem(
                problem,
                production_model,
                single_bin_model
                )
            sat = initialised_model.solve(args=args)
            end = time.perf_counter()

            bench_save = BenchmarkSave(str(problem.json_dict), sat, initialised_model)
            file_directory = os.path.join(os.getcwd(), "results")
            file_name = os.path.join(file_directory, problem.name + ".pickle")

            if not os.path.exists(file_directory):
                os.makedirs(file_directory)

            with open(file_name, 'wb') as handle:
                pickle.dump(bench_save, handle, protocol=pickle.HIGHEST_PROTOCOL)

            print("SAT", sat)
            print("TIME", end-start)

            if sat:
                stats = initialised_model.get_stats()
                stats["total_time"] = end-start

                print("STATS", stats)
                file_name = os.path.join(file_directory, problem.name + ".json")
                with open(file_name, 'w') as handle:
                    handle.write(json.dumps(stats, indent=4))

                #show_bin_packing(initialised_model.single_bin_packing)
                initialised_model.visualise()
                plt.savefig(os.path.join(file_directory, problem.name + '.png'))

                plt.show()




    



