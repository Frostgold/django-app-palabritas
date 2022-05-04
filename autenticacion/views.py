from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .forms import registro
from .models import Usuario

def registration(request):

    context = {}
    context['form'] = registro

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = registro(request.POST)
        password = request.POST['password']

        try:
            # check whether it's valid:
            validate_password(password, user=Usuario)
            if form.is_valid():

                print(form)
                
                new_user = form.save(commit=False) #Save form without commiting
                new_user.password = make_password(new_user.password) #Encrypt password
                new_user.save()

                return HttpResponse("<h1>Gracias por registrarte</h1>")

            else:
                context['form'] = form
        
        except ValidationError as e:
            #form.add_error('password', "Formato del campo incorrecto")
            form.add_error('password', e)
            context['form'] = form

    return render(request, 'registration/registration.html', context)