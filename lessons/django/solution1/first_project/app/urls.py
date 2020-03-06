from django.urls import path

from .views import home_view, workdir_view, time_view

urlpatterns = [
    path('', home_view, name='home'),
    path('current_time/', time_view, name='time'),
    path('workdir/', workdir_view, name='workdir')
]
