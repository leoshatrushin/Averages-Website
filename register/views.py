from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from main.models import *

def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():

            valid = True
            username = form.cleaned_data['username']
            for class_ in Class.objects.all():
                if username == class_.code:
                    valid = False
            if valid:

                new_user = form.save()
                #messages.info(response, "Thanks for registering. You are now logged in.")
                new_user = authenticate(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        )
                login(response, new_user)
            
                return redirect("/choose_subjects/")

            return render(response, "register/register.html", {"form":form})

        return render(response, "register/register.html", {"form":form})
    else:
        form = RegisterForm()

    return render(response, "register/register.html", {"form":form})