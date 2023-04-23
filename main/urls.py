from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('process/', views.process, name='process'),
    path('find/<int:spectrum_id>/', views.find, name='find'),
    path('add/', views.add, name='add'),
    path('search/', views.search, name='search'),
    path('', views.menu, name='menu'),
    path('database_management/', views.database_management, name='database_management'),
    path('delete/', views.delete, name='delete'),
]

urlpatterns += staticfiles_urlpatterns()

