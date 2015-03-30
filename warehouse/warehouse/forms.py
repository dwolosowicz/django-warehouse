from django import forms

class ReviewForm(forms.Form):
    date = forms.DateField()
