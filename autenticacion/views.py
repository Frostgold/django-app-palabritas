from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib.auth import logout

from .forms import Registro

def inicio_view(request):
    return render(request, 'inicio.html')

def registration_view(request):

    context = {}
    context['form'] = Registro

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Registro(request.POST)

        try:
            # check whether it's valid:
            if form.is_valid():
                
                form.save()

                return HttpResponse("<h1>Gracias por registrarte</h1>")

            else:
                context['form'] = form
        
        except ValidationError as e:
            form.add_error('password', e)
            context['form'] = form

    return render(request, 'registration/registration_form.html', context)

def logout_view(request):
    logout(request)
    return redirect('inicio')