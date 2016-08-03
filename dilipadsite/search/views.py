from datetime import date
from haystack.views import SearchView
from search.forms import AdvancedSearchForm
from digg_paginator import DiggPaginator
from django.core.paginator import InvalidPage

class AdvancedSearchView(SearchView):

    def __init__(self, *args, **kwargs):

        if kwargs.get('form_class') is None:
            kwargs['form_class'] = AdvancedSearchForm

        super(AdvancedSearchView, self).__init__(*args, **kwargs)

    def get_start_date(self):
        """
        Returns the query provided by the user.
        Returns an empty string if the query is invalid.
        """
        if self.form.is_valid():
            return self.form.cleaned_data['ed']

        return ''

    def get_end_date(self):
        """
        Returns the query provided by the user.
        Returns an empty string if the query is invalid.
        """
        if self.form.is_valid():
            return self.form.cleaned_data['ed']

        return ''

    def get_pictures(self):
        """
        Returns the query provided by the user.
        Returns an empty string if the query is invalid.
        """
        self.get_results()

    
    def extra_context(self):
        """
        Allows the addition of more context variables as needed.
        Must return a dictionary.
        """
        extra = super(AdvancedSearchView, self).extra_context()
        
        return (extra)

    def build_page(self):

        try:
            page_no = int(self.request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise Http404("Not a valid number for page.")

        if page_no < 1:
            raise Http404("Pages should be 1 or greater.")
        
        paginator = DiggPaginator(self.results, 20, body=5, tail=2, padding=2)

        try:
            page = paginator.page(page_no)
        except InvalidPage:
            raise Http404("Problem with search results (no such page)!")

        return (paginator, page)
        
