
class ResultIterator(object):
    pass

class Indexer(object):
    ID_SLOT = 0
    DATE_SLOT = 1
    PATH_SLOT = 2
    CONTENT_SLOT = 3
    
    def search(self): pass
    def add_document(self, doc): pass
    def remove_document(self, id): pass
     