from django.db import models


class Article(models.Model):

    title = models.CharField(max_length=256, verbose_name='Название')
    text = models.TextField(verbose_name='Текст')
    published_at = models.DateTimeField(verbose_name='Дата публикации')
    image = models.ImageField(null=True, blank=True, verbose_name='Изображение')

    class Meta:
        db_table = 'articles'
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title


class Scope(models.Model):

    topic = models.CharField(max_length=32, verbose_name='Раздел')
    articles = models.ManyToManyField(
        Article, related_name='scopes', through='ArticleScope')

    class Meta:
        db_table = 'scopes'
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return self.topic


class ArticleScope(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    scope = models.ForeignKey(Scope, on_delete=models.CASCADE, verbose_name='Раздел')
    is_main = models.BooleanField(default=False, verbose_name='Основной')

    class Meta:
        db_table = 'articles_scopes'
        verbose_name = 'Раздел статьи'
        verbose_name_plural = 'Разделы статьи'
        ordering = ['-is_main', 'scope__topic']
        default_related_name = 'tags'

    def __str__(self):
        return f'Тэг; { "Основной" if self.is_main else "Второстепенный"}; {self.scope.topic}'
