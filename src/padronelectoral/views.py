from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django import forms
from .models import Elector, Province, District, Canton
from django.views.generic.detail import DetailView
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

def get_province_data(request):
    if request.method == 'GET':
        totalM = 0
        totalF = 0
        totalE = 0

        prov = request.GET.get('prov')
        elector_list = Elector.objects.filter(codelec__canton__province = prov)
        for e in elector_list:
           if e.gender == 1:
               totalM +=1
               totalE +=1
           else:
               totalF +=1
               totalE +=1

        location = elector_list[0].codelec.canton.province
    '''
    elector_prov = Elector.objects.filter(codelec__canton__province=prov)
    m = elector_prov.filter(gender=1).count()
    f = elector_prov.filter(gender=2).count()
    total = elector_prov.count()
    prov = Province.object.all().aggregate(
        sumfemale=Count(canton_district_codelec_gender=2),
        summale=Count(canton_district_codelec_gender=1))

    prov.sumfemale
    prov.summale 
    '''
    return render(request,'stats.html',{'totalM':totalM,'totalF':totalF,'totalE':totalE,'location':location})

def get_canton_data(request):
    if request.method == 'GET':
        totalM = 0
        totalF = 0
        totalE = 0

        cant = request.GET.get('cant')
        elector_list = Elector.objects.filter(codelec__canton = cant)
        for e in elector_list:
           if e.gender == 1:
               totalM +=1
               totalE +=1
           else:
               totalF +=1
               totalE +=1

        location = elector_list[0].codelec.canton

    return render(request,'stats.html',{'totalM':totalM,'totalF':totalF,'totalE':totalE,'location':location})

def get_district_data(request, pk):
    district = get_object_or_404(District, pk=pk)
    if district.stats_total == -1:
        print ("CALCULANDO" )
        elector_list = Elector.objects.filter(codelec = pk)
        district.stats_female = elector_list.filter(gender=2).count()
        district.stats_male = elector_list.filter(gender=1).count()
        district.stats_total = district.stats_female+district.stats_male
        district.save()
    return render(request,'stats.html',{'totalM': district.stats_male,
                                    'totalF': district.stats_female,
                                    'totalE': district.stats_total,
                                    'location':district})



class CantonForm(forms.ModelForm):
    alcalde = forms.CharField()

    # def save(self, *args):
    #     # do something
    #     # self.instance
    #     instance =  super(CantonForm, self).save(*args)
    #     instance.alcalde = self.cleaned_data['alcalde']
    #     return instance
    class Meta:
        model = Canton
        fields = '__all__'
from django.forms import modelform_factory

class CantonView(DetailView):
    template_name = 'canton_template.html'
    model = Canton

    def get_context_data(self, **kwargs):
        context = super(CantonView, self).get_context_data(**kwargs)
        context['districts'] = context['object'].district_set.all()
        context['form'] = CantonForm()
        context['formdist'] = modelform_factory(District,
                                                exclude=('stats_female', 'stats_male'),
                                                fields='__all__')
        return context
