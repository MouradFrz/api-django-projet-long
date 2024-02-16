from django.urls import path
from . import views


urlpatterns = [
    path("get-user-docs", views.get_user_docs),
    path("upload-fichier", views.upload_fichier),
    path("telecharger-fichier/<int:fichier_id>", views.telecharger_fichier),
    path("supprimer-fichier/<int:id>", views.supprimier_fichier),
    path("get-candidatures", views.get_candidatures),
    path("supprimer-candidature/<int:id>", views.supprimer_candidature),
    path("get-candidature/<int:id>", views.get_candidature_ens),
    path("accepter-candidature/<int:id>", views.accepter_candidature),
    path("refuser-candidature/<int:id>", views.refuser_candidature),
    path("get-candidatures-ens", views.get_candidatures_ens),
    path("envoyer-candidature/<int:idformation>", views.envoyer_candidature),
]
