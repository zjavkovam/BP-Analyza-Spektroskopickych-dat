from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('process/', views.process, name='process'),
    path('find/<int:spectrum_id>/', views.find, name='find'),
    path('add/', views.add, name='add'),
    path('search/', views.search, name='search'),
]

urlpatterns += staticfiles_urlpatterns()