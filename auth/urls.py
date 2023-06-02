from django.urls import path

from .views import SignupFormView, LoginFormView, LogoutView, ChangePasswordView, ResetPasswordConfirmView, \
    ResetPasswordDoneView, ResetPasswordView

urlpatterns = [
    path('signup/', SignupFormView.as_view(), name='signup'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password/done/', ResetPasswordDoneView.as_view(), name='reset-password-done'),
    path('reset-password/confirm/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
]
