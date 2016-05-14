import datetime, re
from haystack import indexes
from dilipadsite.models import basehansard

class BaseHansardIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    hid = indexes.CharField(model_attr='hid', indexed=False)
    speechtext = indexes.CharField(model_attr='speechtext')
    opid = indexes.CharField(model_attr='opid', indexed=False)
    pid = indexes.CharField(model_attr='pid', indexed=False, null=True)
    speechdate = indexes.DateField(model_attr='speechdate')
    speakername = indexes.CharField(model_attr='speakername')
    speakerparty = indexes.CharField(model_attr='speakerparty', null=True)
    speakerriding = indexes.CharField(model_attr='speakerriding', null=True)
    speakerposition = indexes.CharField(model_attr='speakerposition', null=True)
    maintopic = indexes.CharField(model_attr='maintopic', null=True)
    subtopic = indexes.CharField(model_attr='subtopic', null=True)
    
    def get_model(self):
        return basehansard
