from django.shortcuts import render

# Create your views here.


def loadIndex(request):
    cantons = []

    return render(request, 'index.html',{'cantonsList': cantons})