from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def runModel(request):
    return render(request, 'runModel.html')