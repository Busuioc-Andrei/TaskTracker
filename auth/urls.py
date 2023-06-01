from django.urls import path

from .views import SignupFormView, LoginFormView, LogoutView, ChangePasswordView

urlpatterns = [
    path('signup/', SignupFormView.as_view(), name='signup'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
