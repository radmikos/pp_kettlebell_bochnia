# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.index, name='index'),
#     path('category/<str:category_name>/', views.category_view, name='category_view'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('amator-kobiety-do-65kg/', views.amator_kobiety_do_65kg, name='amator_kobiety_do_65kg'),
    path('amator-kobiety-powyzej-65kg/', views.amator_kobiety_powyzej_65kg, name='amator_kobiety_powyzej_65kg'),
    path('amator-mezczyzni-do-85kg/', views.amator_mezczyzni_do_85kg, name='amator_mezczyzni_do_85kg'),
    path('amator-mezczyzni-powyzej-85kg/', views.amator_mezczyzni_powyzej_85kg, name='amator_mezczyzni_powyzej_85kg'),
    path('masters-kobiety/', views.masters_kobiety, name='masters_kobiety'),
    path('masters-mezczyzni/', views.masters_mezczyzni, name='masters_mezczyzni'),
    path('najlepsza-bochnianka/', views.najlepsza_bochnianka, name='najlepsza_bochnianka'),
    path('najlepszy-bochnianin/', views.najlepszy_bochnianin, name='najlepszy_bochnianin'),
    path('pro-kobiety/', views.pro_kobiety, name='pro_kobiety'),
    path('pro-mezczyzni-do-85kg/', views.pro_mezczyzni_do_85kg, name='pro_mezczyzni_do_85kg'),
    path('pro-mezczyzni-powyzej-85kg/', views.pro_mezczyzni_powyzej_85kg, name='pro_mezczyzni_powyzej_85kg'),
]