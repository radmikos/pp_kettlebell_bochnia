from django.urls import path
from kettlebell_app.tournament import views

urlpatterns = [
    path('', views.index, name='index'),

]