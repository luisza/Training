from django.shortcuts import render
from .models import Elector
from .forms import SearchForm
# Create your views here.


def loadIndex(request):
    cantons = []
    return render(request, 'index.html',{'cantonsList': cantons})


def viewStats(request):
    stats = []
    return render(request,'stats.html',{'stats':stats})



def get_electors(request):
    if request.method=='POST':
        elector_list = []
        data = request.POST.get('input')
        try:
            data_id = int(data)
            elector_list = Elector.objects.filter(idCard__startswith=data_id)

        except:
            elector_list = Elector.objects.filter(fullName__istartswith = data)

        return render(request,'index.html',{'info':elector_list})