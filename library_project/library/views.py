import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Book, Author, BookInstance
from .forms import RenewBookForm


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
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'library/book_renew.html', context)
