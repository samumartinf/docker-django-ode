import os
import sys
from .models import SimulationResult, Experiment
from django.core.files import File
from django.conf import settings
from celery import shared_task
from scipy.integrate import solve_ivp
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Category20
from bokeh.models import HoverTool

import pandas as pd

# ODE composer stuff
from ode_composer.statespace_model import StateSpaceModel
from ode_composer.dictionary_builder import DictionaryBuilder
from ode_composer.sbl import SBL
import numpy as np
import sympy as sym
from ode_composer.signal_preprocessor import (
    GPSignalPreprocessor,
    SplineSignalPreprocessor,
)


@shared_task
def adding_task(x, y):
    return x + y


@shared_task
def find_structure(file_path, experiment_pk, title, preprocessor=None):
    os.chdir(settings.EXPERIMENTS_URL)
    path, file = os.path.split(file_path)

    try:
        df = pd.read_csv(file)
        t = df['t']

        original_data = {}
        data_dict = {}
        initial_conditions = []
        col_list = []
        derivatives_dict = {}
        std_dict = {}
        for col in df.columns:
            if not col == 't':
                x_data = df[col]
                original_data[f"{col} orig."] = x_data.tolist()
                col_list.append(col)
                initial_conditions.append(x_data[0])

                # step 0: GP Signal preprocessor
                if preprocessor == 'GP':
                    proc = GPSignalPreprocessor(t=t, y=x_data, selected_kernel="RatQuad")
                    y_samples, t_gp = proc.interpolate(return_extended_time=True, noisy_obs=True)
                    proc.calculate_time_derivative()
                    dydt = proc.dydt

                elif preprocessor == 'SP':
                    proc = SplineSignalPreprocessor(t=t, y=x_data)
                    y_samples = proc.interpolate(t)
                    dydt = proc.calculate_time_derivative(t)

                else:
                    y_samples = x_data
                    dydt = np.gradient(x_data)


                if preprocessor == 'GP':
                    dy_std = proc.A_std
                else:
                    dy_std = 0.1  # Placeholder value

                # Populate dictionary
                key_string = col
                data_dict[key_string] = y_samples.T
                derivatives_dict[key_string] = dydt
                std_dict[key_string] = dy_std

        # step 1: define a dictionary
        max_order = 2
        from itertools import combinations_with_replacement
        d_f = []
        print(col_list)

        # Find all possible entries of polynomial order max_order or less
        for i in range(1, max_order + 1):
            tmp = ['*'.join(map(str, x)) for x in combinations_with_replacement(col_list, i)]
            for entry in tmp:
                d_f.append(entry)
        # d_f.append('1')
        print(d_f)
        dict_builder = DictionaryBuilder(dict_fcns=d_f)

        # step 2 define an SBL problem with the Lin reg model and solve it
        dict_mtx = dict_builder.evaluate_dict(input_data=data_dict)
        sbl_dict = {}
        zero_th = 1e-3

        dict_functions = dict_builder.dict_fcns

        for key in data_dict.keys():
            lambda_param = np.sqrt(np.linalg.norm(std_dict[key])) + 0.1
            sbl = SBL(
                dict_mtx=dict_mtx, data_vec=derivatives_dict[key], lambda_param=lambda_param, dict_fcns=dict_functions
            )
            sbl.compute_model_structure()
            sbl_dict[key] = sbl.get_results(zero_th=zero_th)


        # step 4 reporting
        # build the ODE
        ode_model = StateSpaceModel.from_sbl(sbl_dict, parameters=None)
        print("Estimated ODE model:")
        print(ode_model)
        ode_model_str = str(ode_model)

        # TODO: Catch error if no solution is found
        states = col_list
        t_plot = t.tolist()
        sol_ode = solve_ivp(
            fun=ode_model.get_rhs,
            t_span=(t_plot[0], t_plot[-1]),
            t_eval=t_plot, y0=initial_conditions,
            args=(states,)
        )

        plot_dict = dict(zip(states, sol_ode.y.tolist())) #Make list to ensure JSON serializable
        plot_dict = {**original_data, **plot_dict}
        plot_dict['t'] = t_plot

        # print(sbl_dict)
        # results_df = pd.DataFrame(sbl_dict)
        # os.chdir(settings.RESULTS_URL)

        # experiment = Experiment.objects.get(pk=experiment_pk)
        # results_df.to_csv(file)
        # temp_file = open(file)
        # result_file = File(temp_file)

        # result = SimulationResult(
        #     title=title,
        #     experiment=experiment,
        #     result_file=result_file,
        #     signal_preprocessor=preprocessor
        # )

        # result.save()
        # result_file.close()
        # temp_file.close()


        return plot_dict, ode_model_str,

    except IOError as e:
        print(e)
        return 155

    return 0
