from django.shortcuts import render

# Create your views here.

posts = [
    {
        'author': 'CoreyMS',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'August 27, 2019'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'August 27, 2019'

    }
]


def home(request):
    context = {
        'posts': posts
    }
    return render(request, 'system/home.html', context)

def about(request):
    return render(request, 'system/about.html', {'title': 'About'})

def newTrade(request):
    return render(request, 'system/newTrade.html', {'title': 'New Trade'})
