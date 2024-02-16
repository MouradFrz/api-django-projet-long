from django.urls import path
from . import views

urlpatterns = [
    path("api/token/", views.login, name="token_obtain_pair"),
    path("api/token/refresh/", views.refresh, name="token_refresh"),
    path("me", views.me),
    path("get-confirmation-link", views.get_verification_link),
    path("validate-email/<str:id>/<str:confirmation_token>", views.validate_email),
    path("create", views.create),
    path("get-user", views.get_user),
    path("update-pfp", views.update_pfp),
    path("update", views.update),
    path("password/get-reset", views.get_reset),
    path("password/reset/<str:uid>/<str:token>", views.reset_password),
    path("logout", views.logout),
]
