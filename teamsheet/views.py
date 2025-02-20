from django.shortcuts import render

# Create your views here.
def teamsheet(request):
    return render(request, 'teamsheet/teamsheet.html')