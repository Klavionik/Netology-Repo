from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label='Отзыв')

    class Meta:
        model = Review
        exclude = ('id', 'product')
