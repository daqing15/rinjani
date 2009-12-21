
url_handlers = [
    (r"/", 'handlers.home.HomeHandler'),
    (r"/search", 'handlers.misc.SearchHandler'),
    (r"/tweets", 'handlers.misc.TweetsHandler'),
    (r"/l/(\w+)", 'handlers.locale.SetHandler'),
    (r"/survey", 'handlers.misc.SurveyHandler'),
    (r"/getloc", 'handlers.misc.GetLocHandler'),
    
    (r"/talk/new/([\w\-]+)", 'handlers.talk.NewHandler'),
    (r"/talk/updates/([\w\-]+)", 'handlers.talk.UpdatesHandler'),
    (r"/talk/([\w\-]+)", 'handlers.talk.MainHandler'),

    (r"/dashboard", 'handlers.profile.DashboardHandler'),
    (r"/preferences", 'handlers.profile.PreferenceHandler'),
    (r"/users", 'handlers.profile.UserListHandler'),
    (r"/profile/edit", 'handlers.profile.EditHandler'),
    (r"/profile/verify", 'handlers.profile.VerifyHandler'),
    (r"/profile/follow/([\w]+)", 'handlers.profile.FollowHandler'),
    (r"/profile/([\w]+)/followers", 'handlers.profile.FollowersHandler'),
    (r"/profile/([\w]+)/donations", 'handlers.donation.ListHandler'),
    (r"/profile/([\w]+)/about", 'handlers.profile.AboutHandler'),
    (r"/profile/([\w]+)/(activities|articles|pages)", 'handlers.profile.ContentHandler'),
    (r"/profile/([\w]+)", 'handlers.profile.ProfileHandler'),
    
    (r"/admin/?([\w\-]*)/?([\w\-]*)/?([\w\-]*)", 'handlers.admin.RouteHandler'),

    (r"/register", 'handlers.auth.RegisterHandler'),
    (r"/new-user", 'handlers.auth.NewUserHandler'),
    
    (r"/articles/?(latest|featured|popular)?", r'handlers.article.ListHandler'),
    (r"/activities/?(latest|featured|popular)?", r'handlers.activity.ListHandler'),
    (r"/(activity|article|page|post)/new", r'handlers.\1.EditHandler'),
    (r"/(activity|article|page|post)/edit/([\w\-]+)", r'handlers.\1.EditHandler'),
    (r"/(activity|article|page|post)/edit", r'handlers.\1.EditHandler'),
    (r"/(activity|article|page|post)/remove/([\w\-]+)", r'handlers.\1.RemoveHandler'),
    (r"/(activity|article|page|post)/([\w\-]+)", r'handlers.\1.ViewHandler'),
    
    (r"/donation/confirm/([\w\-]+)", 'handlers.donation.ConfirmHandler'),
    (r"/attachment/add", 'handlers.attachment.AddHandler'),
    (r"/attachment/remove", 'handlers.attachment.RemoveHandler'),

    (r"/(content|user)/tagged/([\-\w\+]+)", 'handlers.tag.ViewHandler'),
    (r"/tagged/([\-\w\+]+)", 'handlers.tag.ViewHandler'),
    (r"/tags/?(content|user)?", 'handlers.tag.ListHandler'),
    
    (r"/login/fb", 'handlers.auth.FacebookLoginHandler'),
    (r"/login/google", 'handlers.auth.GoogleLoginHandler'),
    (r"/login/twitter", 'handlers.auth.TwitterLoginHandler'),
    (r"/login", 'handlers.auth.LoginFormHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]
