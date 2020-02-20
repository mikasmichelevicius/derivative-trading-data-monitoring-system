from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='system-home'),
    path('about/', views.about, name='system-about'),
    path('newtrade/', views.newTrade, name='system-newTrade'),

]
