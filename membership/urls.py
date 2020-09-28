from django.urls import path, re_path

from . import views

app_name = 'membership'
urlpatterns = [
    # Membership
    path('', views.PaymentView.as_view(), name='payhome'),
    path('charge/', views.charge, name='charge'),

    # Donation
    path('donateapp/', views.DonateView.as_view(), name='donateapp'),
    path('donateapp/<int:donateamt>/', views.DonateView.as_view(), name='donateapp'),
    path('donate/', views.donate, name='donate'),
    path('donate/<int:donateamt>/', views.donate, name='donate'),
    # path('getdonation/', views.getdonation, name='getdonation'),
    # re_path(r'^(?P<member>[A-Za-z]+)/partner_home/', views.partner_home, name='partner_home'),
    path('browsegen/', views.browsegen, name='browsegen'),
    path('browse/', views.browse, name='browse'),
    path('species/', views.species, name='species'),
    path('hybrid/', views.hybrid, name='hybrid'),
]
