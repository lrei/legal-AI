from django.shortcuts import render, get_object_or_404
from .models import Article
from django.http import HttpResponse
from django.template import loader

def index(request):

    previous_articles = Article.objects.order_by("-articleNum")[:5]
    context = {"previous_articles":previous_articles}

    return render(request, "aiact/index.html", context)

def detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, "aiact/detail.html", {"article": article})
       
def home(request):
    context = {}
    return render(request, 'aiact/home.html', context)