
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

    (r"/attachment/add", 'handlers.attachment.AddHandler'),
    (r"/attachment/remove", 'handlers.attachment.RemoveHandler'),

    (r"/donation/confirm/([\w\-]+)", 'handlers.donation.ConfirmHandler'),

    (r"/dashboard", 'handlers.profile.DashboardHandler'),
    (r"/preferences", 'handlers.profile.PreferenceHandler'),
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

    (r"/activities/?(latest|featured|popular)?", 'handlers.activity.ListHandler'),
    (r"/activity/new", 'handlers.activity.EditHandler'),
    (r"/activity/edit/([\w\-]+)", 'handlers.activity.EditHandler'),
    (r"/activity/edit", 'handlers.activity.EditHandler'),
    (r"/activity/remove/([\w\-]+)", 'handlers.activity.RemoveHandler'),
    (r"/activity/([\w\-]+)", 'handlers.activity.ViewHandler'),

    (r"/articles/?(latest|featured|popular)?", 'handlers.article.ListHandler'),
    (r"/article/new", 'handlers.article.EditHandler'),
    (r"/article/edit/([\w\-]+)", 'handlers.article.EditHandler'),
    (r"/article/edit", 'handlers.article.EditHandler'),
    (r"/article/remove/([\w\-]+)", 'handlers.article.RemoveHandler'),
    (r"/article/([\w\-]+)", 'handlers.article.ViewHandler'),

    (r"/page/new", 'handlers.page.EditHandler'),
    (r"/page/edit/([\w\-]+)", 'handlers.page.EditHandler'),
    (r"/page/edit", 'handlers.page.EditHandler'),
    (r"/page/([\w\-]+)", 'handlers.page.ViewHandler'),

    (r"/users", 'handlers.profile.UserListHandler'),

    (r"/(content|user)/tagged/([\-\w\+]+)", 'handlers.tag.ViewHandler'),
    (r"/tagged/([\-\w\+]+)", 'handlers.tag.ViewHandler'),
    (r"/tags/?(content|user)?", 'handlers.tag.ListHandler'),
    
    (r"/flag", 'handlers.tag.FlagHandler'),
    (r"/report", 'handlers.report.Handler'),

    (r"/login/fb", 'handlers.auth.FacebookLoginHandler'),
    (r"/login/google", 'handlers.auth.GoogleLoginHandler'),
    (r"/login/twitter", 'handlers.auth.TwitterLoginHandler'),
    (r"/login", 'handlers.auth.LoginFormHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]
