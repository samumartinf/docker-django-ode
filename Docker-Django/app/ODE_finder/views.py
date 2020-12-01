import os
from celery import current_app
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .tasks import find_structure
from .forms import ExperimentForm, SimulationForm
from .models import Experiment, SimulationResult
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Category20
from bokeh.models import HoverTool
import random
import json
import numpy as np
import pandas as pd

# Sympy simplification
from sympy import sympify, simplify

def home(request):
    time = np.arange(1000)/500
    parabola = time ** 2
    line = time
    context={}

    ode_model = 'dx/dt = 2x\ndy/dt = 1'

    data_dict = {
        'time': time,
        'x**2': parabola,
        'x': line
    }
    df = pd.DataFrame(data_dict)
    html_table = df.to_html(classes=['table', 'table-striped', 'table-sm', 'table-hover'])

    plot = figure(
        x_axis_label='Time',
        y_axis_label='Value',
        plot_width=1200,
        plot_height=550,
    )
    plot.title.text_font_size='16pt'
    plot.line(time, line, legend_label="y=x", line_width=2.0)
    plot.line(time, parabola, legend_label='y=x^2', color='orange', line_width=2.0)

    script, div = components(plot)
    context = {
        'script': script,
        'div': div,
        'table': html_table,
        'ode_model': ode_model,
    }
    return render(request, "ODE_finder/Bootstrap_home.html",context)

def delete_experiment(request, pk):
    if request.method == "POST":
        experiment = Experiment.objects.get(pk=pk)
        experiment.delete()
    return redirect('experiment_list')


def experiment_list(request):
    experiments = Experiment.objects.all()
    results = SimulationResult.objects.all()

    return render(request, 'ODE_finder/Bootstrap_experiment_list.html', {
        'experiments': experiments,
        'results': results
    })


def simulation_config(request):
    if request.method == "POST":
        form = SimulationForm(request.POST, request.FILES)

        if form.is_valid():
            context = {}
            experiment = form.cleaned_data['experiment']
            preprocessor = form.cleaned_data['signal_preprocessor']
            title = form.cleaned_data['title']

            task = find_structure.delay(
                file_path=experiment.csv_file.url,
                experiment_pk=experiment.pk,
                title=title,
                preprocessor=preprocessor
            )
            request.session['task_id'] = task.id
            print(task.id)

            return redirect('test_view')

    else:
        form = SimulationForm()

    return render(request, 'ODE_finder/Bootstrap_simulation_config.html', {
        'form': form
    })


def upload_experiment(request):
    if request.method == "POST":
        form = ExperimentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            experiment = Experiment.objects.latest('upload_date')
            file_path = experiment.csv_file.url
            print(file_path)
            return redirect('simulation_config')
    else:
        form = ExperimentForm()

# TODO: Migrate this from test_old to the new html template
    return render(request, 'ODE_finder/Bootstrap_upload.html', {
        'form': form
    })


def results_view(request):
    task_id = None
    experiment_pk = None
    try:
        task_id = request.session['task_id']
        task = current_app.AsyncResult(request.session['task_id'])
    except:
        pass

    if task_id is None:
        return redirect('experiment_list')

    context = {'task_status': task.status, 'task_id': task.id}

    if task.status == 'SUCCESS':
        results_dict, ode_strings = task.get() #results is a dictionary and ode_strings
        time = results_dict['t']
        plot = figure(
            title='Retrieved ODE',
            x_axis_label='Time',
            y_axis_label='Value',
        )
        for key, color in zip(results_dict, Category20[len(results_dict.keys())]):
            if key != 't':
                plot.line(time, results_dict[key], legend_label=f"{key}", color=color, line_width=2.0)
        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        plot.sizing_mode = "stretch_both"
        script, div = components(plot)
        context['script'] = script
        context['div'] = div
        context['ode_string'] = ode_strings

        print(context['ode_string'])

    return render(request, 'ODE_finder/Bootstrap_home.html', context)


def test_view(request):
    context = {}
    task_id = None
    experiment_pk = None
    try:
        task_id = request.session['task_id']
        task = current_app.AsyncResult(request.session['task_id'])
        context['task_id'] = task.id
        task_dict = {"task_id" : task_id, "task_status": task.status}
        context["task"] = json.dumps(task_dict)
    except:
        pass

    if task.status == 'SUCCESS':
        results_dict, ode_strings = task.get() #results is a dictionary and ode_strings
        time = results_dict['t']
        plot = figure(
            x_axis_label='Time',
            y_axis_label='Value',
            plot_width=1200,
            plot_height=550,
        )
        for key, color in zip(results_dict, Category20[len(results_dict.keys())]):
            if key != 't':
                if 'orig.' in key:
                    plot.line(time, results_dict[key], legend_label=f"{key}", color=color, line_width=2.0, line_dash='dashed')
                else: 
                    plot.line(time, results_dict[key], legend_label=f"{key}", color=color, line_width=2.0)
        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        script, div = components(plot)
        df = pd.DataFrame(results_dict)
        html_table = df.to_html(classes=['table', 'table-striped', 'table-sm', 'table-hover'])

        context['script'] = script
        context['div'] = div
        context['ode_model'] = ode_strings
        context['table'] = html_table

    return render(request, 'ODE_finder/Bootstrap_results.html', context)


class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            response_data['results'] = task.get()

        return JsonResponse(response_data)
