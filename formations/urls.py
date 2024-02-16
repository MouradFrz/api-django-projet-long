# formations/urls.py

from django.urls import path, include
from .views import liste_formations, ajouter_formation, modifier_formation, supprimer_formation, liste_modules, ajouter_module, modifier_module, supprimer_module,ajouter_chapitre, modifier_chapitre, supprimer_chapitre,liste_chapitres
from rest_framework import routers
from django.urls import path
from . import views

urlpatterns = [

path('', views.liste_formations, name='liste_formations'),
path('ajouter/', views.ajouter_formation, name='ajouter_formation'),
path('modifier/<int:formation_id>/', views.modifier_formation, name='modifier_formation'),
path('supprimer/<int:formation_id>/', views.supprimer_formation, name='supprimer_formation'),
path('mes-etudiants',views.get_etudiants_de_ma_formation,name="mes_etudiants"),
path('<int:id>',views.formation, name='formation'),

path('liste_modules/<int:formation_id>/', views.liste_modules, name='liste_modules'),
path('liste_modules',views.list_module_pour_ens,name="liste_module_pour_ens"),
path('modules/<int:module_id>', views.module_complet, name='module_complet'),
path('modules/ajouter/', views.ajouter_module, name='ajouter_module'),
path('modules/ajouter-fichier/<int:chapitre_id>/', views.ajouter_fichier, name='ajouter_fichier'),
path('modules/supprimer-fichier/<int:id>/', views.supprimer_fichier, name='supprimer_fichier'),
path('modules/telecharger-fichier/<int:fichier_id>/', views.telecharger_fichier, name='telecharger_fichier'),
path('modules/modifier/<int:formation_id>/<int:module_id>/', views.modifier_module, name='modifier_module'),
path('modules/supprimer/<int:module_id>/', views.supprimer_module, name='supprimer_module'),
path('modules/set-responsable/<int:id>',views.set_responsable),

path('module/<int:module_id>/liste_chapitres/', views.liste_chapitres, name='liste_chapitres'),
path('module/<int:module_id>/ajouter_chapitre/', views.ajouter_chapitre, name='ajouter_chapitre'),
path('modules/chapitres/<int:chapitre_id>/modifier/', views.modifier_chapitre, name='modifier_chapitre'),
path('modules/chapitres/<int:chapitre_id>/supprimer/', views.supprimer_chapitre, name='supprimer_chapitre'),
]