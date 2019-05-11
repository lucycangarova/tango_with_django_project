from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required 
from datetime import datetime
from rango.webhose_search import run_query
from django.contrib.auth.models import User

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
	last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now())) 
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S') 
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

def index(request):
	request.session.set_test_cookie() 
	# Query the database for a list of ALL categories currently stored. 
	# Order the categories by no. likes in descending order. 
	# Retrieve the top 5 only - or all if less than 5. 
	# Place the list in our context_dict dictionary 
	# that will be passed to the template engine. 
	category_list = Category.objects.order_by('-likes')[:5] 
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list} 

	visitor_cookie_handler(request) 
	context_dict['visits'] = request.session['visits']

	# Render the response and send it back! 
	response = render(request, 'rango/index.html', context_dict)

	# Return response back to the user, updating any cookies that need changed. 
	return response

def about(request):
	if request.session.test_cookie_worked(): 
		print("TEST COOKIE WORKED!") 
		request.session.delete_test_cookie()

	context_dict = {'boldmessage' : "Lucia Cangarova"}

	visitor_cookie_handler(request) 
	context_dict['visits'] = request.session['visits']
	
	return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug): 
	# Create a context dictionary which we can pass 
	# to the template rendering engine. 
	context_dict = {}

	try: 
		# Can we find a category name slug with the given name? 
		# If we can't, the .get() method raises a DoesNotExist exception. 
		# So the .get() method returns one model instance or raises an exception. 
		category = Category.objects.get(slug=category_name_slug)

		# Retrieve all of the associated pages. 
		# Note that filter() will return a list of page objects or an empty list
		pages = Page.objects.filter(category=category).order_by('-views')

		# Adds our results list to the template context under name pages. 
		context_dict['pages'] = pages 
		# We also add the category object from # the database to the context dictionary. 
		# We'll use this in the template to verify that the category exists. 
		context_dict['category'] = category 

	except Category.DoesNotExist:
		# the template will display the "no category" message for us. 
		context_dict['category'] = None 
		context_dict['pages'] = None

	context_dict['query'] = category.name

	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run our Webhose search function to get the results list!
			result_list = run_query(query)
			context_dict['query'] = query
			context_dict['result_list'] = result_list

	# Go render the response and return it to the client. 
	return render(request, 'rango/category.html', context_dict) 

def add_category(request):
	form = CategoryForm()

	#if HTTP POST
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			#confirmation message, redirect to index page
			return index(request)
		else:
			print(form.errors)
	return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug = category_name_slug)
	except Ctageoty.DoesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)

	context_dict = {'form':form, 'category' : category}
	return render(request, 'rango/add_page.html', context_dict)

@login_required
def register_profile(request):
	profile_form = UserProfileForm()

	if request.method == 'POST':
		profile_form = UserProfileForm(request.POST, request.FILES)

		if profile_form.is_valid():
			profile = profile_form.save(commit=False)
			profile.user = request.user
			profile.save()

			return redirect('rango:index')
		else:
			# Invalid form
			print(profile_form.errors) 

	return render(request, 'rango/profile_registration.html', {'profile_form': profile_form}) 


'''def register(request):
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST) 
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save() 
			user.set_password(user.password) 
			user.save()

			profile = profile_form.save(commit=False) 
			profile.user = user

			if 'picture' in request.FILES: 
				profile.picture = request.FILES['picture'] 

			profile.save()

			registered = True
		else:
			# Invalid form
			print(user_form.errors, profile_form.errors) 

	else:
		# These forms will be blank, ready for user input. 
		user_form = UserForm() 
		profile_form = UserProfileForm()

	return render(request, 'rango/register.html', 
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered}) 

def user_login(request):

	if request.method == 'POST':
		username = request.POST.get('username') 
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user: 
			if user.is_active:
				login(request, user) 
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your Rango account is disabled.") 
		else:
			print("Invalid login details: {0}, {1}".format(username, password)) 
			return render(request, 'rango/login.html', {'message': 'Invalid login details supplied.'}) 

	else:
		return render(request, 'rango/login.html', {}) 
'''
@login_required 
def restricted(request): 
	return render(request, 'rango/restricted.html', {})
'''
@login_required 
def user_logout(request): 
	# Since we know the user is logged in, we can now just log them out. 
	logout(request) 
	# Take the user back to the homepage. 
	return HttpResponseRedirect(reverse('index')) 
'''

def search(request):
	context_dict = {}
	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run our Webhose search function to get the results list!
			result_list = run_query(query)
			context_dict['query'] = query
	context_dict['result_list'] = result_list
	return render(request, 'rango/search.html', context_dict)

def track_url(request):
	page_id = None
	url = '/rango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url
			except:
				pass
	return redirect(url)

@login_required
def profile(request, username):
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		return redirect('index')

	userprofile = UserProfile.objects.get_or_create(user=user)[0]
	form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})

	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
		if form.is_valid():
			form.save(commit=True)
			return redirect('rango:profile', user.username)
		else:
			print(form.errors)

	return render(request, 'rango/profile.html',{'userprofile': userprofile, 'selecteduser': user, 'form': form})


def users(request):
	context_dict = {}

	users = UserProfile.objects.all();
	context_dict['users'] = users

	return render(request, 'rango/users.html', context_dict)

@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
		likes = 0
		if cat_id:
			cat = Category.objects.get(id=int(cat_id))
			if cat:
				likes = cat.likes + 1
				cat.likes = likes
				cat.save()
	return HttpResponse(likes)

def get_category_list(max_results=0, starts_with=''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__istartswith=starts_with)
	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]
	return cat_list

def suggest_category(request):
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']
	cat_list = get_category_list(8, starts_with)
	return render(request, 'rango/cats.html', {'cats': cat_list })

@login_required
def auto_add_page(request):
	cat_id = None
	url = None
	title = None
	context_dict = {}
	if request.method == 'GET':
		cat_id = request.GET['category_id']
		url = request.GET['url']
		title = request.GET['title']
		if cat_id:
			category = Category.objects.get(id=int(cat_id))
			p = Page.objects.get_or_create(category=category,title=title, url=url)
			pages = Page.objects.filter(category=category).order_by('-views')
			# Adds our results list to the template context under name pages.
			context_dict['pages'] = pages
	return render(request, 'rango/page_list.html', context_dict)
