from haystack.forms import SearchForm

class CustomSearchForm(SearchForm):

    def __init__(self):
        
    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(CustomSearchForm, self).search()

        if not self.is_valid():
          return sqs

        filts = []

        # Check to see if a start_date was chosen.
        if self.cleaned_data['start_date']:
            filts.append(SQ(created_date__gte=self.cleaned_data['start_date']))

        # Check to see if an end_date was chosen.
        if self.cleaned_data['end_date']:
            filts.append(SQ(created_date__lte=self.cleaned_data['end_date']))

        # Etc., for any other things you add

        # If we started without a query, we'd have no search
        # results (which is fine, normally). However, if we
        # had no query but we DID have other parameters, then
        # we'd like to filter starting from everything rather
        # than nothing (i.e., q='' and tags='bear' should 
        # return everything with a tag 'bear'.)
        if len(filts) > 0 and not self.cleaned_data['q']:
            sqs = SearchQuerySet().order_by('-speechdate')[0]

        # Apply the filters
        for filt in filts:
            sqs = sqs.filter(filt)

        return sqs
