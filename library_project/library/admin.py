from django.contrib import admin

# Register your models here.

from .models import Author, Genre, Language, Book, BookInstance


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


# Define the admin class
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # with pass the admin behavior will be unchanged
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]


class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'borrower', 'due_back')
    list_display = ('id', 'book', 'imprint', 'display_status')
    fieldsets = (
        (None, {
            'fields': ('id', 'book', 'imprint')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        })
    )


# Register the admin class with the associated model
# admin.site.register(Book, BookAdmin) alternative if not using @admin.register(Book)
admin.site.register(Language)
admin.site.register(Genre)
