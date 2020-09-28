"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

from accounts.views import login_page, register_page, update_profile, index
# from accounts.views import LoginView, RegisterView, guest_register_view
from django.urls import path, include
from myproject.views import orchid_home, home, private_home
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', orchid_home, name='orchid_home'),
    path('home/', orchid_home, name='orchid_home'),
    path('private_home/', private_home, name='private_home'),

    path('admin/', admin.site.urls),
    # path('select2/', include('select2.urls')),

    path('index/', index, name='index'),
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('update_profile/', update_profile, name='update_profile'),
    path('logout/', LogoutView.as_view(), {'next_page': '//'}, name='logout'),
    # path('password_reset/', include(password_reset.urls)),

    # Experiment
    # API
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    # Test Django-Q, restAPI, Redis
    path('genera/', include('genera.urls')),

    path('documents/', include('documents.urls')),
    path('detail/', include('detail.urls')),
    path('orchidlist/', include('orchidlist.urls')),
    path('search/', include('search.urls')),

    # Decommissioned
    # path('membership/', include('membership.urls')),
    # path('partnership/', include('partnership.urls')),

    # Legacy
    path('orchid/', include('orchid.urls')),
    path('natural/', include('natural.urls')),
    path('orchidlite/', include('orchidlite.urls')),

    # Control
    path('robots.txt', TemplateView.as_view(template_name="myproject/robots.txt", content_type='text/plain')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)