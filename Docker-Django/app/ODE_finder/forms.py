from django import forms
from .models import Experiment, SimulationResult

class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('title', 'author', 'csv_file')


class SimulationForm(forms.ModelForm):
    class Meta:
        model = SimulationResult
        fields = ('title', 'experiment', 'signal_preprocessor')

