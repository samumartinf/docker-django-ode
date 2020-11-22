# thumbnailer/urls.py
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
  path('experiments/', views.experiment_list, name='experiment_list'),
  path('experiments/upload/', views.upload_experiment, name='upload_experiment'),
  path('experiments/<int:pk>/', views.delete_experiment, name='delete_experiment'),
  path('experiments/simulate/', views.simulation_config, name='simulation_config'),
  path('experiments/results/', views.results_view, name='results_view'),
  path('test/', views.test_view, name='test_view'),
  path('task/<str:task_id>/', views.TaskView.as_view(), name='task'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
