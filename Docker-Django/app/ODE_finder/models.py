import datetime

from django.db import models
from .validators import validate_csv_extension


# Create your models here.
class Experiment(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    csv_file = models.FileField(
        upload_to='experiments/',
        max_length=100,
        validators=[validate_csv_extension]
    )
    upload_date = models.DateTimeField('date uploaded', auto_now=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.csv_file.delete()
        super().delete(*args, **kwargs)


class SimulationResult(models.Model):
    # Choices preparation
    GP = 'GP'
    SPLN = 'SP'
    NONE = 'NA'

    PREPROCESSOR_CHOICES = [
        (GP, 'Gaussian Process'),
        (SPLN, 'Spline'),
        (NONE, 'None')
    ]

    # Model fields
    title = models.CharField(max_length=200)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    result_file = models.FileField(upload_to='results/', max_length=100)
    signal_preprocessor = models.CharField(
        max_length=2,
        choices=PREPROCESSOR_CHOICES,
        default=SPLN,
    )
    simulation_date = models.DateTimeField('date simulated', auto_now=True)

    # Model modifiers
    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.result_file.delete()
        super().delete(*args, **kwargs)
