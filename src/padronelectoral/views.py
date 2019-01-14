from django.shortcuts import render
from django.views import generic
from .models import Elector
from .forms import SearchForm
# Create your views here.


class IndexView(generic.FormView):
    template_name = 'index.html'

    def get_elector(request):
        if request.method == 'POST':
            context_object_name = 'elector_list'
            form_class = SearchForm()
            data = request.POST.get('input')
            elector_list = []
            # check if input data is either number or string
            try:
                data_id = int(data)
                elector_list = Elector.objects.filter(idCard__startswith=data_id)


            except:
                elector_list = Elector.objects.filter(fullName__istartswith=data)

        return render(request, 'index.html', {'info': elector_list,'form':form_class})






