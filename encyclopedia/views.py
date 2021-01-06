from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from markdown2 import Markdown
import secrets

from . import util

# Represents a form that the user can use to create a new encyclopedia entry
class NewpageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "class" : "form-control col-md-8 col-lg-8", 
        "placeholder": "Enter page content here"
    }))

# Represents a form that the user can use to edit an existing entry
class EditForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "class" : "form-control col-md-8 col-lg-8"
    }))

# EFFECTS: render the default page for the application
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# EFFECTS: if an entry with the given title DNE, render an error page
#          otherwise, convert the entry from MD to HTML and render page
def entry(request, title):
    entryMD = util.get_entry(title)
    if (entryMD == None):
        return render(request, "encyclopedia/entryNotFound.html", {
            "title": title
        })

    markdowner = Markdown()
    entryHTML = markdowner.convert(entryMD)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": entryHTML
    })

# EFFECTS: if POST request, save the new page
#          otherwise, render page where user can create a new encyclopedia entry
def newpage(request):
    if request.method == "POST":
        return saveNewpage(request)

    return render(request, "encyclopedia/newpage.html", {
        "newpageForm": NewpageForm()
    })

# EFFECTS: if form is valid
#               1. and an encyclopedia entry already exists with the given title, produce an error message
#               2. othewise, save the encyclopedia entry and redirect to the new entry's page
#          otherwise, reload the page with the same form
# Error messages: https://docs.djangoproject.com/en/3.1/ref/contrib/messages/
# Error message styling: https://getbootstrap.com/docs/4.0/components/alerts/
def saveNewpage(request):
    form = NewpageForm(request.POST)

    if form.is_valid():
        title = form.cleaned_data["title"]
        
        if title in util.list_entries():
            msg = f"Entry for '{ title }' already exists. Your new entry will not be saved."
            messages.error(request, msg)
            return render(request, "encyclopedia/newpage.html", {
                "newpageForm": form
            })
        
        content = form.cleaned_data["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=[title]))
    else: 
        return render(request, "encyclopedia/newpage.html", {
            "newpageForm": form
        })

# EFFECTS: if POST request, save the edits to the entry
#          otherwise, render page where user can make edits to existing entry
# Adding initial form data: https://www.geeksforgeeks.org/initial-form-data-django-forms/
def edit(request, title):
    if request.method == "POST":
        return saveEdits(request, title)

    initialData = {
        "content": util.get_entry(title)
    }

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "editForm": EditForm(initial = initialData)
    })

# EFFECTS: if form is valid, save edits and redirect to the entry's page
#          otherwise, reload the page with the same form
def saveEdits(request, title):
    form = EditForm(request.POST)

    if form.is_valid():
        content = form.cleaned_data["content"]

        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("entry", args=[title]))
    else: 
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "editForm": form
        })

# EFFECTS: if the query matches an encyclopedia entry, redirect to that page
#          otherwise, display search results page with all encyclopedia entries which have the 
#          query as a substring
def search(request):
    query = request.GET["q"]
    entries = util.list_entries()

    if query in entries:
        return HttpResponseRedirect(reverse("entry", args=[query]))
    
    relevantEntries = findRelevantEntries(entries, query)
    return render(request, "encyclopedia/index.html", {
        "query": query,
        "entries": relevantEntries,
        "search": True
    })

# EFFECTS: returns a list of the titles of entries which query is a substring of
def findRelevantEntries(entries, query):
    relevantEntries = []

    for entry in entries:
        if query.upper() in entry.upper():
            relevantEntries.append(entry)
    return relevantEntries

# EFFECTS: selects a random entry from the list of entries and redirects to the entry's page
def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)

    return HttpResponseRedirect(reverse("entry", args=[randomEntry]))
