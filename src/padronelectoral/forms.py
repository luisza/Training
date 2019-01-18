from django import forms
from .models import Elector
class SearchForm(forms.Form):
    input = forms.CharField(max_length=100)


class ElectorForm(forms.ModelForm):
    class Meta:
        model=Elector
        fields = ['idCard','fullName','gender','cad_date','codelec','board',]


