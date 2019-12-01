from django.urls import path
from . import views

urlpatterns = [
        path('', views.default_map, name='default'),
]
