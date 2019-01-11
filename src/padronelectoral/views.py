from django.shortcuts import render

# Create your views here.
from padronelectoral.models import Elector


def loadIndex(request):
    cantons = []
    return render(request, 'index.html',{'cantonsList': cantons})


def viewStats(request):
    stats = []
    return render(request,'stats.html',{'stats':stats})


def searchPerson(request):
    input = request.POST.get('input')
    filter = {}
    try:
        #beacause this variable by default is string. So I try to cast to int in case that this variable
        #is an ID or except when this is a name or last name
        inputToInt = int(input)
        filter = {'id':inputToInt}
    except:
        filter = {'name':input}

    print(filter)

    elector = Elector()
    elector.idCard = 34590943
#    elector.codelec = 102033
    elector.junta = 1
    lista = []
    lista.append(elector)

    return render(request, 'index.html', {'info': lista})