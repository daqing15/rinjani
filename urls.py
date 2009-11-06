
url_handlers = [
    (r"/", 'handlers.home.HomeHandler'),
    (r"/l/(\w+)", 'handlers.main.LocaleHandler'),
    (r"/attachment/add", 'handlers.attachment.AddHandler'),
    (r"/attachment/remove", 'handlers.attachment.RemoveHandler'),
    
    (r"/donation/confirm/([A-Za-z0-9\-]+)", 'handlers.donation.ConfirmHandler'),
    
    (r"/account", 'handlers.profile.AccountHandler'),
    (r"/profile/edit", 'handlers.profile.EditHandler'),
    (r"/profile/donations", 'handlers.donation.ListHandler'),
    (r"/profile/comments", 'handlers.profile.CommentsHandler'),
    (r"/profile/comments/([A-Za-z0-9\.]+)", 'handlers.profile.ProfileCommentsHandler'),
    (r"/profile/articles/([A-Za-z0-9\.]+)", 'handlers.profile.ArticlesHandler'),
    (r"/profile/activities/([A-Za-z0-9\.]+)", 'handlers.profile.ActivitiesHandler'),
    (r"/profile/([A-Za-z0-9\.]+)", 'handlers.profile.ViewHandler'),
    
    (r"/register", 'handlers.profile.RegisterHandler'),
    (r"/new-user", 'handlers.profile.NewUserHandler'),
    (r"/dashboard", 'handlers.profile.Dashboard'),
    
    (r"/activities", 'handlers.activity.ListHandler'),
    (r"/activity/new", 'handlers.activity.EditHandler'),
    (r"/activity/edit/([A-Za-z0-9\-]+)", 'handlers.activity.EditHandler'),
    (r"/activity/edit", 'handlers.activity.EditHandler'),
    (r"/activity/remove/([A-Za-z0-9\-]+)", 'handlers.activity.RemoveHandler'),
    (r"/activity/([0-9]{4}/[0-9]{1,2}/[0-9]{1,2})/([A-Za-z0-9\-]+)", 'handlers.activity.ViewHandler'),
    
    (r"/articles", 'handlers.article.ListHandler'),
    (r"/article/new", 'handlers.article.EditHandler'),
    (r"/article/edit/([A-Za-z0-9\-]+)", 'handlers.article.EditHandler'),
    (r"/article/edit", 'handlers.article.EditHandler'),
    (r"/article/remove/([A-Za-z0-9\-]+)", 'handlers.article.RemoveHandler'),
    (r"/article/([0-9]{4}/[0-9]{1,2}/[0-9]{1,2})/([A-Za-z0-9\-]+)", 'handlers.article.ViewHandler'),
    
    (r"/page/new", 'handlers.page.EditHandler'),
    (r"/page/edit/([A-Za-z0-9\-]+)", 'handlers.page.EditHandler'),
    (r"/page/edit", 'handlers.page.EditHandler'),
    (r"/page/([A-Za-z0-9\-]+)", 'handlers.page.ViewHandler'),
    
    (r"/users", 'handlers.profile.UserListHandler'),
    
    (r"/tag/is/([a-z0-9]+)", 'handlers.tag.ViewHandler'),
    (r"/tags", 'handlers.tag.ListHandler'),
    
    (r"/report", 'handlers.report.Handler'),
    
    (r"/login/fb", 'handlers.auth.FacebookLoginHandler'),
    #(r"/login/google", 'handlers.auth.GoogleLoginHandler'),
    #(r"/login/twitter", 'handlers.auth.GoogleLoginHandler'),
    (r"/login-form", 'handlers.auth.LoginFormHandler'),
    (r"/login", 'handlers.auth.LoginHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]
