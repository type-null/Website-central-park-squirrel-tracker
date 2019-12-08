from django.urls import path

from . import views

urlpatterns = [
    path('', views.list, name='list'),
    path('add/', views.add, name='add'),
    path('stats/', views.stats, name='stats'),
    path('<squirrel_id>/', views.update, name='update'),
    path('<squirrel_id>/delete/', views.delete, name='delete'),
]
