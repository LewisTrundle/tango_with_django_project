from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from django.shortcuts import redirect
from django.urls import reverse

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


def add_category(request):
    form = CategoryForm()
    
    # An HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # Checks form is valid
        if form.is_valid():
            # saves the new category to database
            form.save(commit=True)
            # Redirects user back to index view.
            return redirect('/rango/')
        else:
            # If form contained errors, prints them to terminal.
            print(form.errors)
            
    # Will handle the bad/new/no form supplied cases
    # Renders the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        
    # You cannot add a page to a Category that doesn't exist...
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
    
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
            
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)