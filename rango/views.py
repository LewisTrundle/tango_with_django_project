from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

def index(request):
    # Order categories by likes descending order
    # Rretrieve top 5 only
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list


    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    #return HttpResponse("Rango says here is the about page. \
#<a href='/rango/'>Index</a>")
    
    context_dict = {'boldmessage': 'This tutorial has been put together by Lewis Trundle'}
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    
    try:
        # Tries to find category name slug with given name
        # If it can't, the get() method raises DoesNotExist exception
        # get() methods returns one model instance or raises exception
        category = Category.objects.get(slug=category_name_slug)
        
        # Retreives all associated pages
        # filter() returns list of page objects or empty list
        pages = Page.objects.filter(category=category)
        
        # Adds results list to template context under name pages
        context_dict['pages'] = pages
        # Adds category object from database to dict - used to verify category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # If specified category can't be found, template will display "no category" message
        context_dict['category'] = None
        context_dict['pages'] = None
        
    # renders and returns response to client
    return render(request, 'rango/category.html', context=context_dict)