from django.shortcuts import render

# Create your views here.
def about_page_view(request):
    return render(request, 'pages/about.html')

def home_page_view(request):
    return render(request, 'pages/home.html')
