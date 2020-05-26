
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.Home.as_view(), name="home"),
    path('login',views.loginUser, name="login"),
    # path('change_password',views.ChangePassword, name="change passsword"),
    path('logout',views.logoutUser, name="logout"),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
         name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
         name='password_change'),

    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('register/', views.register, name = 'register'),
    path('shopkeeper-reg/', views.shopkeeper_reg, name = "shopkeeper-reg"),
    path('oauth/', include('social_django.urls', namespace='social')),

    path('address/', views.address, name='address'),
    path('product/<int:pk>/', views.ItemDetailView.as_view(), name='product'),

]
