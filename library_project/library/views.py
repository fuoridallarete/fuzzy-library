from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Book, Author, BookInstance


# Create your views here.

@login_required
def index(request):
    num_books = Book.objects.all().count
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status='a').count()

    # .all() is implied by default
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits
    }
    template = 'library/index.html'

    # Render the HTML template index.html with the data in the context variable
    return render(request, template, context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model: Book
    # add code below to customise, otherwise just above line is enough to make the view work
    # your own name for the list as a template variable
    context_object_name = 'books_list'

    # Get 5 books containing the title war
    queryset = Book.objects.all()
    # Specify your own template name/location
    # template_name = 'books/my_arbitrary_template_name_list.html'
    '''
        We might also override get_context_data() in order to pass additional context variables to the template (e.g. 
        the list of books is passed by default). The fragment below shows how to add a variable named "some_data" to the 
        context (it would then be available as a template variable):
        
        def get_context_data(self, **kwargs):
            # Call the base implementation first to get the context
            context = super(BookListView, self).get_context_data(**kwargs)
            # Create any data and add it to the context
            context['some_data'] = 'This is just some data'
            return context
            
        When doing this it is important to follow the pattern used above:
    
        1. First get the existing context from our superclass.
        2. Then add your new context information.
        3. Then return the new (updated) context.
    '''


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model = Book
    context_object_name = 'book'


class AuthorListView(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model: Author
    # add code below to customise, otherwise just above line is enough to make the view work
    # your own name for the list as a template variable
    context_object_name = 'authors_list'

    # Get 5 books containing the title war
    queryset = Author.objects.all()


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    model = Author
    context_object_name = 'author'
