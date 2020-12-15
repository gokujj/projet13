from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.log_in, name="log_in"),
    path('logout/', views.log_out, name="log_out"),
    path('register/', views.register, name="register"),
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path(
        'password-forgotten/',
        views.password_forgotten,
        name="password_forgotten",
    ),
    path(
        'password-reset-activate/<uidb64>/<token>/',
        views.password_reset_activate,
        name="password_reset_activate",
    ),
    path(
        'password-reset/', views.password_reset_new, name="password_reset_new"
    ),
]