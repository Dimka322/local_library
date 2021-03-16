import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import RenewBookModelForm
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django import forms


# Create your views here.

def index(request: HttpRequest):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genres = Genre.objects.count()
    # num_books_with = Book.objects.filter(title='Война и Мир').count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={'num_books': num_books,
                 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,
                 'num_genres': num_genres,
                 'num_visits': num_visits,
                 # 'num_books_with': num_books_with,
                 }
    )


class BookListView(generic.ListView):
    model = Book
    # context_object_name = 'my_book_list'
    # queryset = Book.objects.filter(title__contains='Война')[:5]
    # queryset = Book.objects.all()[:5]
    # template_name = 'books/my_arbitrary_template_name_list.html'
    paginate_by = 2


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    # context_object_name = 'my_author_list'
    # queryset = Author.objects.all()[:5]
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserlistView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksByStuffListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookModelForm(request.POST)

        if form.is_valid():

            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'renewal_date': proposed_renewal_date, })

    return render(
        request,
        'catalog/book_renew_librarian.html',
        context={
            'form': form,
            'bookinst': book_inst
        }
    )


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '12/10/2016'}


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy = ('authors')


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'genre', 'isbn', 'language']
    initial = {'language': 'Русский'}


class BookUpdate(UpdateView):
    model = Book
    fields = ['author', 'summary', 'genre', 'language']


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy = ('books')
