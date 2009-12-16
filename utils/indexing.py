"""
Schema defined in /conf/peduli-solr/conf/schema.xml
"""

from settings import SOLR_URL
from pythonsolr.pythonsolr import Solr, solr_batch_adder 
from models import Content, User
import simplejson
import time
          
"""
 <fields>
   <field name="id" type="string" indexed="true" stored="true" required="true" /> 
   <field name="title" type="text" indexed="true" stored="true" required="true" />
   <field name="path" type="text" indexed="false" stored="true" />
   <field name="type" type="int" indexed="true" stored="true" />
   
   <!-- extra fields stored in 'meta' as json string -->
   <field name="meta" type="raw" indexed="false" stored="true" />
   
   <!-- local lucene field types -->
   <field name="lat" type="sdouble" indexed="true" stored="true"/><!-- must match the latField in solrconfig.xml -->
   <field name="lng" type="sdouble" indexed="true" stored="true"/><!-- must match the lngField in solrconfig.xml -->
   <field name="geo_distance" type="sdouble"/> <!-- Optional but used for distributed searching -->
   <dynamicField name="_local*" type="sdouble" indexed="true" stored="true"/><!-- used internally by localsolr -->
   
   <field name="tags" type="lowercase" indexed="true" stored="true" multiValued="true" omitNorms="true" />
   <field name="content" type="text" indexed="true" stored="true" compressed="true" />
   <field name="created_at" type="date" indexed="true" stored="true" multiValued="false"/>
   <field name="updated_at" type="date" indexed="true" multiValued="false" />
   <field name="timestamp" type="date" indexed="true" stored="true" default="NOW" multiValued="false" />
   <dynamicField name="*" type="ignored" multiValued="true" />
 </fields>
"""    

class SolrIndex:
    src = [
           (Content, [
                ('id', '_id'), 'title', 'tags',
                'created_at', 'updated_at', 'content',
                ('path', lambda o: o.get_url()),
                ('type', lambda o: int(o['type'])),
            ]), 
           (User, [
                ('id', '_id'), ('title', lambda o: o['fullname'] or o['username']), 
                'tags', 'created_at', 'updated_at',
                ('content', lambda o: o['profile_content'] or o['about']),
                ('path', lambda o: o.get_url()),
                ('type', lambda o: 6),
            ])
        ]
    def __init__(self, url=SOLR_URL):
        self.solr = Solr(url)
    
    def add(self, doc):
        self.solr.add(doc)
    
    def delete(self, id=None, query=None):
        self.delete(id, query)
    
    def search(self, query, **kwargs):
        return self.solr.search(query, **kwargs)
    
    def runcmd(self, cmd, **kwargs):
        c = getattr(self.solr, cmd, None)
        if c:
            c(kwargs)
            
    def rebuild_index(self):
        alldocs = []
        start = time.time()
        
        for doccls, fields in self.src:
            docs = doccls.all()
            for doc in docs:
                _doc = {}
                for field in fields:
                    if type(field) == str:
                        _doc[field] = doc[field]
                    elif type(field) == tuple:
                        if callable(field[1]):
                            _doc[field[0]] =  field[1](doc)
                        else:
                            _doc[field[0]] = doc[field[1]]
                        
                alldocs.append(_doc)
                
        with solr_batch_adder(self.solr) as batcher:
            for doc in alldocs:
                batcher.add_one(doc)
        
        print "FInished processing %d docs in %f" % (len(alldocs), time.time()-start)

def generate_doc_content():
    import re
    from string import truncate_words
    from markov import MarkovGenerator
    from models import Content, User
    import markdown2
    import genericng

    m = MarkovGenerator(2)
    txt = file('/rinjani/var/data/tomsawyer.txt').read()
    txt = re.sub('["*]*-', '', txt)
    m.learn(txt)
    names = []
    for cls in [Content]:
        total = cls.collection.find().count()
        i = 0
        while i < total:
            docs = cls.all().skip(i).limit(20)
            for doc in docs:
                print "Generating for " + doc['_id'] + "...",
                field = 'profile_content' if doc.has_key('profile_content')\
                            else 'content'
                if isinstance(doc, Content):
                    doc['title'] = re.sub("[!.;:]+","", truncate_words(m.say().title(), 6)[0:60]).title()
                else:
                    name = genericng.generate(3,7)
                    while name in names:
                        name =  genericng.generate(2)
                    doc['username'] = name
                    names.append(name)
                    
                doc[field] = ".\n\n".join([(m.say().title()) for _i in range(6)])
                if field == 'content':
                    doc['excerpt'] = m.say()
                doc[field + "_html"] = markdown2.markdown(doc[field])
                doc.save()
                print "done. Saved."
            del(docs)
            i += 20

index = SolrIndex()
