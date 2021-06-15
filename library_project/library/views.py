import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .forms import RenewBookModelForm
from .models import Book, Author, BookInstance
from .forms_one import RenewBookForm


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


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'library/user_books.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('library.can_mark_returned', raise_exception=True)
def library_status(request):
    num_available = BookInstance.objects.filter(status='a').count()
    num_on_maintenance = BookInstance.objects.filter(status='m').count()
    num_on_loan = BookInstance.objects.filter(status='o').count()
    num_reserved = BookInstance.objects.filter(status='r').count()

    context = {
        'num_available': num_available,
        'num_on_maintenance': num_on_maintenance,
        'num_on_loan': num_on_loan,
        'num_reserved': num_reserved
    }
    template = 'library/library_status.html'

    # Render the HTML template index.html with the data in the context variable
    return render(request, template, context=context)


class LoanedBooksListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    permission_required = 'library.can_mark_returned'
    model: BookInstance
    context_object_name = 'on_loan_books_list'

    # Get 5 books containing the title war
    queryset = BookInstance.objects.filter(status__exact='o').order_by('due_back')
    template_name = 'library/books_on_loan.html'
    paginate_by = 10


class AvailableBooksListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    permission_required = 'library.can_mark_returned'
    model: BookInstance
    context_object_name = 'available_books_list'

    # Get 5 books containing the title war
    queryset = BookInstance.objects.filter(status__exact='a').order_by('due_back')
    template_name = 'library/books_available.html'
    paginate_by = 10


class MaintenanceBooksListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    permission_required = 'library.can_mark_returned'
    model: BookInstance
    context_object_name = 'maintenance_books_list'

    # Get 5 books containing the title war
    queryset = BookInstance.objects.filter(status__exact='m').order_by('due_back')
    template_name = 'library/books_on_maintenance.html'
    paginate_by = 10


class ReservedBooksListView(PermissionRequiredMixin, LoginRequiredMixin, generic.ListView):
    permission_required = 'library.can_mark_returned'
    model: BookInstance
    context_object_name = 'reserved_books_list'

    # Get 5 books containing the title war
    queryset = BookInstance.objects.filter(status__exact='r').order_by('due_back')
    template_name = 'library/reserved_books.html'
    paginate_by = 10


def renew_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        # if using forms_one.py
        # form = RenewBookForm(request.POST)

        # if using forms.py
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # if using forms_one.py
            # book_instance.due_back = form.cleaned_data['renewal_date']

            # if using forms.py
            book_instance.due_back = form.cleaned_data['due_back']

            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('books_on_loan'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # if using forms_one.py
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

        # if using forms.py
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'library/book_renew.html', context)

# The "create" and "update" views use the same template by default, which will be named
# after your model: model_name_form.html (you can change the suffix to something other
# than _form using the template_name_suffix field in your view, for example
# template_name_suffix = '_other_suffix')


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'library.can_mark_returned'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    # You can also specify initial values for each of the fields using a
    # dictionary of field_name / value pairs, ex:
    # initial = {'date_of_death': '11/06/2020'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'library.can_mark_returned'
    model = Author
    fields = '__all__'  # Not recommended (potential security issue if more fields added)


# By default, these views (create, update, delete) will redirect on success to a page displaying the newly
    # created/edited model item, which in our case will be the author detail view.
    # You can specify an alternative redirect location by explicitly declaring parameter success_url,
    # see AuthorDelete class.

# The "delete" view expects to find a template named with the format
# model_name_confirm_delete.html (again, you can change the suffix using
# template_name_suffix in your view).

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'library.can_mark_returned'
    model = Author
    # The AuthorDelete class doesn't need to display any of the fields, so these don't need to be specified.
    # You do however need to specify the success_url, because there is no obvious default value for Django to use.
    # In this case, we use the reverse_lazy() function to redirect to our author list after an author has been deleted
    # — reverse_lazy() is a lazily executed version of reverse(), used here because we're providing a URL
    # to a class-based view attribute.
    success_url = reverse_lazy('authors')
