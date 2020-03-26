from django.views.generic import ListView

from articles.models import Article


class ArticlesView(ListView):
    template_name = 'articles/news.html'
    queryset = Article.objects.prefetch_related()
