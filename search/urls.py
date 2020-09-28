from django.urls import path, re_path
from . import views

app_name = 'search'
urlpatterns = [
    # Top level
    path('search_match/', views.search_match, name='search_match'),
    path('search_fuzzy/', views.search_fuzzy, name='search_fuzzy'),
    path('nomenclature/', views.nomenclature, name='nomenclature'),
    re_path(r'^(?P<partner>[A-Za-z]+)/search_match/', views.search_match, name='search_match'),
    re_path(r'^(?P<partner>[A-Za-z]+)/search_fuzzy/', views.search_fuzzy, name='search_fuzzy'),
]
