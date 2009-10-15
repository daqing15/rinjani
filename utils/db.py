
def ensure_indexes(db):
    db.users.ensure_index('username')
    db.articles.ensure_index('slug', None, True)