from django.shortcuts import render

from articles.models import Article


def articles_list(request):
    template = 'articles/news.html'
    articles = Article.objects.prefetch_related().all()
    objects_list = []

    for index, article in enumerate(articles):
        title = article.title
        text = article.text
        image = article.image
        objects_list.append({
            'title': title,
            'text': text,
            'image': image,
            'scopes': []
        })
        articlescopes = article.articlescopes.all()
        for articlescope in articlescopes:
            objects_list[index]['scopes'].append(
                {
                    'topic': articlescope.scope.topic,
                    'is_main': articlescope.is_main
                })

    context = {'object_list': objects_list}

    return render(request, template, context)
