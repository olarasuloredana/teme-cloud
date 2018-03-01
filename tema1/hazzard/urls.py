from django.urls import path

from . import views

app_name = 'hazzard'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('choose/', views.choose, name='choose'),
    path('back/', views.back, name='back')
]