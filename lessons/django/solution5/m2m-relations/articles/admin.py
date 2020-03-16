from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import Article, Scope, ArticleScope


class ArticleScopesInlineFormset(BaseInlineFormSet):
    def clean(self):
        main = 0
        for form in self.forms:
            if form.cleaned_data.get('main'):
                main += 1
        if main > 1:
            raise ValidationError("Только один раздел может быть основным!")
        elif main < 1:
            raise ValidationError("Укажите хотя бы один основной раздел!")
        return super().clean()


class ArticleScopesInline(admin.TabularInline):
    model = ArticleScope
    formset = ArticleScopesInlineFormset


@admin.register(Scope)
class ScopeAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticleScopesInline]
