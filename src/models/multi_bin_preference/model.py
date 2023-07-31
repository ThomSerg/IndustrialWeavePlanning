
'''
NOT IN USE !
'''


from __future__ import annotations


from src.data_structures.machine_config import MachineConfig
from src.data_structures.production_schedule import ProductionSchedule


from src.models.abstract_model import AbstractProductionModel
from src.data_structures.problem.multi_bin_problem import MultiBinProblem

from src.models.abstract_model import AbstractSingleBinModel

from src.models.multi_bin.lns.model import LnsMBM


class PreferenceMBM():

    # Constructor
    def __init__(self,
                    machine_config: MachineConfig,
                    production_schedule: ProductionSchedule,
                    production_model: AbstractProductionModel,
                    single_bin_model: AbstractSingleBinModel,
                ):
        
        # Set attributes of self
        self.machine_config = machine_config
        self.production_schedule = production_schedule
        self.production_model = production_model
        self.single_bin_model = single_bin_model

        # Create LNS solver
        self.solver = LnsMBM(
                            self.machine_config,
                            self.production_schedule,
                            self.production_model,
                            self.single_bin_model
                        )

        self.bin_solutions = []
        self.epsilon = 0.2
        self.rho = 1#0.8
        

    # Alternative constructor from problem formulation
    @classmethod
    def init_from_problem(cls, 
                          problem: MultiBinProblem, 
                          production_model: AbstractProductionModel,
                          single_bin_model: AbstractSingleBinModel
                          ) -> PreferenceMBM:
        # Construct the model
        return cls(
            problem.get_machine_config(),
            problem.get_production_schedule(),
            production_model,
            single_bin_model,
        )
    
    # Name of the model
    def get_name():
        return "MultiPreferenceModel"
    
    def set_args(self, args:dict):
        self.args = args

    def solve(self):
        sat, models = self.solver.solve(self.args)  
        self.models = models 
        self.bin_solutions = models[-1].single_bin_solutions
        return sat, models
    
    """
    Return the current preference weights.
    """
    def get_preference(self):
        return self.solver.get_preference()
    
    """
    Reset to uniform preference.
    """
    def reset_preference(self):
        n = len(self.get_preference())
        self.solver.update_preference([1/n]*n)

    """
    Set which preference to improve
    """
    def set_preference_index(self, preference_index: int):
        self.preference_index = preference_index
    
    """
    Update preference weights towards selected index
    """
    def increase_preference(self, objective_index: int):
        # Get current preference
        preference = self.get_preference()
        # Update preference towards selected index
        preference[objective_index] += self.epsilon
        self.epsilon *= self.rho
        # Normalise preference
        s = sum(preference)
        preference = [p/s for p in preference]
        # Propagate preference
        self.solver.update_preference(preference)

    """
    Keep solving untill no improvement towards the preference is found
    """
    def improve(self):
        no_improvement_counter = 0
        no_improvement_limit = 1
        while True:
            sat, models = self.solver.solve(self.args, self.bin_solutions)
            self.models = models
            model = models[-1]
            self.bin_solutions = model.single_bin_solutions

            if (not any(model.bin_production.bin_active[model.bin_production.bin_active.shape[0]-1,:].value())):
                no_improvement_counter += 1
            else:
                no_improvement_counter = 0

            if no_improvement_counter >= no_improvement_limit:
                break

        return sat, models
    

    def improve_preference(self, no_improvement_limit=2):
        improvement = False
        improvement_reference_index = len(self.bin_solutions)-1
        model: AbstractProductionModel = self.models[-1]
        improvement_reference_repeats = model.bin_production.bin_repeats

        while not improvement:
            improvement = False

            self.increase_preference(self.preference_index)
            print("PREFERENCE UPDATE", self.get_preference())

            
            for i_iter in range(no_improvement_limit):
                print("IMPROVEMENT ITERATION", i_iter)
                sat, models = self.solver.solve(self.args, self.bin_solutions)
                model = models[-1]
                self.bin_solutions = model.single_bin_solutions

                if (
                    (model.bin_production.bin_active[improvement_reference_index:,:].value()).any()
                    or
                    (model.bin_production.bin_repeats[:improvement_reference_index+1,:] != improvement_reference_repeats).any()
                    ):
                    improvement = True
                    break
            
        sat, models = self.improve()

        return sat, models

    def get_stats(self):
        return self.production_model.get_stats()
    
    def visualise(self):
        self.production_model.visualise()