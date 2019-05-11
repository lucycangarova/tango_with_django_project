import os 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django 
django.setup() 

from rango.models import Category, Page 

def add_page(cat, title, url, views = 0):
	p = Page.objects.get_or_create(category=cat, title=title)[0]
	p.url=url 
	p.views=views
	p.save()
	return p

def add_cat(name, views = 0, likes = 0):
	c = Category.objects.get_or_create(name=name)[0]
	c.views = views
	c.likes = likes
	c.save()
	return c

def populate(): 
	# First, we will create lists of dictionaries containing the pages
	# we want to add into each category. 
	# Then we will create a dictionary of dictionaries for our categories. 
	# This might seem a little bit confusing, but it allows us to iterate 
	# through each data structure, and add the data to our models.

	python_pages = [
		{"title": "Official Python Tutorial", 
		"url":"http://docs.python.org/2/tutorial/",
		"views":24}, 
		{"title":"How to Think like a Computer Scientist", 
		"url":"http://www.greenteapress.com/thinkpython/",
		"views":26}, 
		{"title":"Learn Python in 10 Minutes",
		"url":"http://www.korokithakis.net/tutorials/python/",
		"views":2} ]

	django_pages = [
		{"title":"Official Django Tutorial",
		"url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/",
		"views":13},
		{"title":"Django Rocks",
		"url":"http://www.djangorocks.com/",
		"views":8},
		{"title":"How to Tango with Django",
		"url":"http://www.tangowithdjango.com/",
		"views":45} ]

	other_pages = [
		{"title":"Bottle",
		"url":"http://bottlepy.org/docs/dev/",
		"views":6},
		{"title":"Flask",
		"url":"http://flask.pocoo.org",
		"views":1}]

	pascal_pages=[{"title":"Tutorials point - Pascal",
		"url":"https://www.tutorialspoint.com/pascal/",
		"views":0},
		{"title":"Pascal Programming",
		"url":"http://www.pascal-programming.info/index.php",
		"views":1}]

	perl_pages=[{"title":"Perl Tutorial for Beginners: Learn in 1 Day",
		"url":"https://www.guru99.com/perl-tutorials.html",
		"views":0},
		{"title":"The Perl Programming",
		"url":"https://www.perl.org/",
		"views":1}]

	php_pages=[{"title":"Learn PHP - Free Interactive PHP Tutorial",
		"url":"https://www.learn-php.org/",
		"views":0},
		{"title":"PHP 5 Tutorial - W3Schools",
		"url":"https://www.w3schools.com/php/",
		"views":0},
		{"title":"PHP: Hypertext Preprocessor",
		"url":"https://php.net/",
		"views":0}]

	prolog_pages=[{"title":"Prolog | An Introduction - GeeksforGeeks",
		"url":"https://www.geeksforgeeks.org/prolog-an-introduction/",
		"views":0},
		{"title":"Introduction to logic programming with Prolog",
		"url":"https://www.matchilling.com/introduction-to-logic-programming-with-prolog/",
		"views":0}]

	postscript_pages=[{"title":"PostScript Tutorial - Paul Bourke",
		"url":"paulbourke.net/dataformats/postscript/",
		"views":0},
		{"title":"Quick PostScript Programming Tutorial",
		"url":"https://www.mostlymaths.net/2008/12/quick-postscript-programming-tutorial.html",
		"views":0}]

	programming_pages=[{"title":"Programming: Online Courses by Harvard, MIT, Microsoft",
		"url":"https://www.edx.org/learn/computer-programming",
		"views":0},
		{"title":"Programming - Codecademy",
		"url":"https://www.codecademy.com/catalog/subject/programming",
		"views":0}]

	cats = {"Python": {"pages": python_pages, "views":128, "likes":64},
		"Django": {"pages": django_pages, "views":64, "likes":32},
		"Other Frameworks": {"pages": other_pages, "views":32, "likes":16}, 
		"Pascal":{"pages":pascal_pages, "views":0, "likes":0}, 
		"Perl":{"pages":perl_pages, "views":0, "likes":0},
		"PHP":{"pages":php_pages, "views":0, "likes":0}, 
		"Prolog":{"pages":prolog_pages, "views":0, "likes":0}, 
		"PostScript":{"pages":postscript_pages, "views":0, "likes":0},
		"Programming":{"pages":programming_pages, "views":0, "likes":0},
		}

	# The code below goes through the cats dictionary, then adds each category,
	# and then adds all the associated pages for that category.

	for cat, cat_data in cats.items():
		c = add_cat(cat, cat_data["views"], cat_data["likes"] )
		for p in cat_data["pages"]:
			add_page(c, p["title"], p["url"], p['views'])

	# Print out the categories we have added. 
	for c in Category.objects.all():
		for p in Page.objects.filter(category=c):
				print("- {0} - {1}".format(str(c), str(p)))

# Start execution here!
if __name__ == '__main__':
	print("Starting Rango population script...")
	populate()