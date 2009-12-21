import tornado.web

from main import BaseHandler, authenticated
from models import Content, User, Page, Donation, BankAccount
from rinjani.pagination import Pagination
from forms import profile_form

class RouteHandler(BaseHandler):
    SORT_FIELDS = {'u': 'username', 'c': 'created_at', 'ap': 'auth_provider', 'l':'last_login'}
    
    @authenticated(None, True)
    def get(self, *args):
        if args[0] == '':
            self.render('admin/dashboard', user=self.current_user)
            return
        else:
            func = getattr(self, args[0], None)
            if func:
                func(*args[1:])
    
    def _sort(self, field, current_by, current_sort):
        if field == current_by and int(current_sort) in [1, -1]:
            return str(-(int(current_sort)))
        return "1"
    
    def users(self, *args):
        sort_by = self.get_argument('sort_by', 'username')
        sort_by = sort_by if sort_by in ['u','c','ap','l'] else 'u'
        sort = int(self.get_argument('sort', 1))
        pagination = Pagination(self, User, None, 
                                sort_by=self.SORT_FIELDS[sort_by], 
                                sort=sort)
        self.render("admin/users", pagination=pagination, by=sort_by, sort=sort, _sort=self._sort)
    
    def user(self, *args):
        user = User.one({'username': args[0]})
        if not user:
            raise tornado.web.HTTPError(404)
            return
        accounts = user.get_bank_accounts()
        accounts = BankAccount.listify(accounts) if accounts.count() else []
        user.formify()
        f = profile_form()
        f.fill(user)
        self.render("admin/user", user=user, accounts=accounts, f=f)
        