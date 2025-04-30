from django import forms
from .models import State

class SearchForm(forms.Form):
    q = forms.CharField(
        label='O que você procura?',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: iPhone, sofá, carro'})
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        label='Estado',
        required=False,
        empty_label="Todo Brasil"
    )