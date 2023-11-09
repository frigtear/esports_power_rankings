from django.shortcuts import render


def display_methodology(request):
    return render(request,'methodology/method.html')