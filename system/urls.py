from django.urls import path
from . import views

app_name = 'system' # for Django to know know which app view create for a url when using {% url %} template tag

urlpatterns = [
    path('', views.home, name='home'),
    path('newtrade/', views.newTrade, name='newTrade'),
    path('viewtrades/', views.viewTrades, name='viewTrades'),
    path('viewrules/',views.viewRules, name='viewRules'),
    path('report/', views.generateReport, name='generateReport'),
    path('print/', views.printReport, name='printReport')

]
