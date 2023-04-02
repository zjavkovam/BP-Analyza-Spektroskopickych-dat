from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('process/', views.process, name='process'),
]

urlpatterns += staticfiles_urlpatterns()