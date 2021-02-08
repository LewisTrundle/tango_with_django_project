from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    # Order categories by likes descending order
    # Retrieve top 5 only
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    visitor_cookie_handler(request)
    
    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Lewis Trundle'}
    
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    
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


@login_required
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


@login_required
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


def register(request):
    # Is registration successful?
    registered = False
    
    if request.method == 'POST':
        # Attempt to grab info from raw form information
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save user's form data to database
            user = user_form.save()
            
            # Set then update password
            user.set_password(user.password)
            user.save()
            
            # Set commit=False to delay saving model
            # until ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # If profile pic provided, get it from input form
            # and put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            # Saves UserProfile instance
            profile.save()
            
            # Update variable to indicate to template registration was successful
            registered = True
        else:
            # Invalid form(s)
            # Prints problems to terminal
            print(user_form.errors, profile_form.errors)
    else:
        # Not an HTTP POST so form rendered using two ModelForm instances
        # These forms will be blank, ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    # Render template depending on context
    return render(request,
                  'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})
    
    
def user_login(request):
    # If request is HTTP POST, try to pull relevant info
    if request.method == 'POST':
        # Get username and password from login form
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # If username/password combination valid, User object is returned
        user = authenticate(username=username, password=password)
        
        # If we have as User object, the details are correct
        # If None, no user with matching credential found
        if user:
            # Is account active?
            if user.is_active:
                # If account valid and active, log user in and send back to homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used so doesn't log in
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details provided, so doesn't log in
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
        
    # The request is not HTTP POST, so display login form
    # This would be HTTP GET
    else:
        # No context variables to pass to template system so blank dict. object
        return render(request, 'rango/login.html')
    
    
@login_required
def restricted(request):
    context_dict = {'message': "Since you're logged in, you can see this text!"}
    
    return render(request, 'rango/restricted.html', context=context_dict)
    #return HttpResponse("Since you're logged in, you can see this text!")


@login_required
def user_logout(request):
    # Since we know user is logged in, we can just log them out
    logout(request)
    # Returns user to homepage
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
    '%Y-%m-%d %H:%M:%S')
    
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
        
    # Update/set the visits cookie
    request.session['visits'] = visits
        
        