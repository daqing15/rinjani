
url_handlers = [
    (r"/", 'handlers.home.HomeHandler'),
    (r"/tweets", 'handlers.misc.TweetsHandler'),
    (r"/l/(\w+)", 'handlers.locale.SetHandler'),
    (r"/survey", 'handlers.misc.SurveyHandler'),
    
    (r"/chat", 'handlers.chat.MainHandler'),
    (r"/chat/new", 'handlers.chat.MessageNewHandler'),
    (r"/chat/updates", 'handlers.chat.MessageUpdatesHandler'),

    (r"/attachment/add", 'handlers.attachment.AddHandler'),
    (r"/attachment/remove", 'handlers.attachment.RemoveHandler'),

    (r"/donation/confirm/([\w\-]+)", 'handlers.donation.ConfirmHandler'),

    (r"/account", 'handlers.profile.AccountHandler'),
    (r"/profile/edit", 'handlers.profile.EditHandler'),
    (r"/profile/verify", 'handlers.profile.VerifyHandler'),
    (r"/profile/follow/([\w]+)", 'handlers.profile.FollowHandler'),
    (r"/profile/followers/([\w]+)", 'handlers.profile.FollowersHandler'),
    (r"/profile/donations", 'handlers.donation.ListHandler'),
    (r"/profile/comments", 'handlers.profile.CommentsHandler'),
    (r"/profile/comments/([\w]+)", 'handlers.profile.ProfileCommentsHandler'),
    (r"/profile/articles/([\w]+)", 'handlers.profile.ArticlesHandler'),
    (r"/profile/activities/([\w]+)", 'handlers.profile.ActivitiesHandler'),
    (r"/profile/([\w]+)", 'handlers.profile.ViewHandler'),

    (r"/register", 'handlers.auth.RegisterHandler'),
    (r"/new-user", 'handlers.auth.NewUserHandler'),
    (r"/dashboard", 'handlers.profile.Dashboard'),

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
    (r"/tags/?(content|user)?", 'handlers.tag.ListHandler'),
    
    (r"/flag", 'handlers.tag.FlagHandler'),
    (r"/report", 'handlers.report.Handler'),

    (r"/login/fb", 'handlers.auth.FacebookLoginHandler'),
    (r"/login/google", 'handlers.auth.GoogleLoginHandler'),
    (r"/login/twitter", 'handlers.auth.TwitterLoginHandler'),
    (r"/login/yahoo", 'handlers.auth.YahooLoginHandler'),
    (r"/login", 'handlers.auth.LoginFormHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]
