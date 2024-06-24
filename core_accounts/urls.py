from django.urls import path
from core_accounts.views import DeleteUserProfile, GoogleUserRegistrationView, PasswordResetRequestView, PasswordResetView, Register, ShowProfile, UpdateProfileView, UserLogin


urlpatterns = [
    path('public/u/register/<str:user_type>/', Register.as_view()),
    path('public/google/auth/', GoogleUserRegistrationView.as_view()),
    path('public/password-rest-request/', PasswordResetRequestView.as_view()),
    path('public/password-rest/', PasswordResetView.as_view()),
    path('public/u/login/', UserLogin.as_view()),
    path('profile/update/', UpdateProfileView.as_view()),
    path('profile/delete/', DeleteUserProfile.as_view()),
    path('profile/delete/', DeleteUserProfile.as_view()),
    path('profile/<int:id>/show/', ShowProfile.as_view()),
]
