from django.contrib import admin

from .models import Experiment, SimulationResult



admin.site.register([SimulationResult, Experiment])