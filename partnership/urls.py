# from django.conf.urls import url, include
from django.urls import path, re_path
from . import views

# TODO: Add a new page: Compare two species/hybrids
# TODO: Add feature search page - search by color, features
# TODO: Add search by ancestors pair.
# TODO: Add search by location

app_name = 'partnership'
urlpatterns = [
    # path('<char:partner>/species/<int:pid>/', views.species, name='species'),
    # path('<char:partner>/hybrid/<int:pid>/', views.hybrids, name='hybrid'),
    re_path(r'^(?P<partner>[A-Za-z]+)/partner_home/', views.partner_home, name='partner_home'),
    re_path(r'^(?P<partner>[A-Za-z]+)/browsegen/', views.browsegen, name='browsegen'),
    re_path(r'^(?P<partner>[A-Za-z]+)/browse/', views.browse, name='browse'),
    re_path(r'^(?P<partner>[A-Za-z]+)/species/', views.species, name='species'),
    re_path(r'^(?P<partner>[A-Za-z]+)/hybrid/', views.hybrid, name='hybrid'),
]
