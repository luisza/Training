from django import forms
from .models import Elector
from django.utils.translation import gettext_lazy as _

class SearchForm(forms.Form):
    input = forms.CharField(max_length=100)


class ElectorForm(forms.ModelForm):
    cad_date = forms.DateField(label="Date")

    def __init__(self, *args, **kwargs):
        super(ElectorForm, self).__init__(*args, **kwargs)
        self.fields['idCard'].label = _("Cédula")

    class Meta:
        model=Elector
        fields = ['idCard','fullName','gender','cad_date','codelec','board',]


