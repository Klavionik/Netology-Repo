from django.urls import path

from articles.views import ArticlesView

urlpatterns = [
    path('', ArticlesView.as_view(), name='articles'),
]
