
url_handlers = [
    (r"/", 'handlers.home.HomeHandler'),
    (r"/l/(\w+)", 'handlers.main.LocaleHandler'),
    
    (r"/donation/confirm/([A-Za-z0-9\-]+)", 'handlers.donation.ConfirmHandler'),
    
    (r"/profile/edit", 'handlers.profile.EditHandler'),
    (r"/profile/donations", 'handlers.donation.ListHandler'),
    (r"/profile/comments", 'handlers.profile.CommentsHandler'),
    (r"/profile/([A-Za-z0-9\.]+)/comments", 'handlers.profile.ProfileCommentsHandler'),
    (r"/profile/([A-Za-z0-9\.]+)", 'handlers.profile.ViewHandler'),
    (r"/register", 'handlers.profile.RegisterHandler'),
    (r"/new_user", 'handlers.profile.RegisterFBHandler'),
    (r"/dashboard", 'handlers.profile.Dashboard'),
    
    (r"/activities", 'handlers.activity.ListHandler'),
    (r"/activity/new", 'handlers.activity.EditHandler'),
    (r"/activity/edit", 'handlers.activity.EditHandler'),
    (r"/activity/edit/([A-Za-z0-9\-]+)", 'handlers.activity.EditHandler'),
    (r"/activity/([A-Za-z0-9\-]+)", 'handlers.activity.ViewHandler'),
    
    (r"/articles", 'handlers.article.ListHandler'),
    (r"/article/new", 'handlers.article.EditHandler'),
    (r"/article/edit", 'handlers.article.EditHandler'),
    (r"/article/edit/([A-Za-z0-9\-]+)", 'handlers.article.EditHandler'),
    (r"/article/([A-Za-z0-9\-]+)", 'handlers.article.ViewHandler'),
    
    (r"/page/new", 'handlers.page.EditHandler'),
    (r"/page/edit", 'handlers.page.EditHandler'),
    (r"/page/edit/(.*)", 'handlers.page.EditHandler'),
    (r"/page/(.*)", 'handlers.page.ViewHandler'),
    
    (r"/users", 'handlers.profile.UserListHandler'),
    
    (r"/tag/is/([a-z0-9]+)", 'handlers.tag.ViewHandler'),
    (r"/tags", 'handlers.tag.ListHandler'),
    
    (r"/report", 'handlers.report.Handler'),
    
    (r"/login/fb", 'handlers.auth.FacebookLoginHandler'),
    (r"/login", 'handlers.auth.LoginHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]
