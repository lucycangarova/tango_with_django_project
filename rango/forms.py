from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
	name = forms.CharField(max_length=128, help_text="Please enter the category name.")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	slug = forms.CharField(widget=forms.HiddenInput(), required=False)

	#additional information on the form
	class Meta:
		#association between the ModelForm and model
		model = Category
		fields = ("name",)


class PageForm(forms.ModelForm):
	title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
	url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

	class Meta:
		#association between ModelForm and model
		model = Page
		#hiding foreign key
		exclude = ("category",)
		#or fields = ('title', 'url','views',) without category field

	def clean(self):
		cleaned_data = self.cleaned_data
		url = cleaned_data.get('url')

		#if url not empty and doesnt start with http
		if url and not url.startswith('http://'):
			url = 'http://' + url
			cleaned_data['url'] = url

			return cleaned_data

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User 
		fields = ('username', 'email', 'password',)

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile 
		fields = ('website', 'picture',)