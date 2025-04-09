from django.urls import path
from .views import UserRegistrationView, ActivateAccountView, RequestPasswordResetView \
  ,ConfirmPasswordResetView, UserLoginView, TokenAuthView

urlpatterns = [
  path('register/', UserRegistrationView.as_view(), name='register'),
  path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
  path('reset-password/', RequestPasswordResetView.as_view(), name='password_reset'),
  path('reset-password/confirm/<str:token>/', ConfirmPasswordResetView.as_view(), name='password_reset_confirm'),
  path('login/', UserLoginView.as_view(), name='login'),
  path('remember-login/', TokenAuthView.as_view(), name='token_login'),
]
