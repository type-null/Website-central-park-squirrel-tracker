from django.urls import path

from . import views

urlpatterns = [
    path('', views.list, name='list'),
    path('<squirrel_id>/', views.update_delete, name='update or delete'),
    path('add/', views.add, name='add'),
    path('stats/', views.stats, name='stats'),
]
