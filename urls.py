
url_handlers = [
    (r"/", 'handlers.home.HomeHandler'),
    (r"/tweets", 'handlers.misc.TweetsHandler'),
    (r"/l/(\w+)", 'handlers.locale.SetHandler'),
    (r"/survey", 'handlers.misc.SurveyHandler'),

    (r"/attachment/add", 'handlers.attachment.AddHandler'),
    (r"/attachment/remove", 'handlers.attachment.RemoveHandler'),

    (r"/donation/confirm/([A-Za-z0-9\-]+)", 'handlers.donation.ConfirmHandler'),

    (r"/account", 'handlers.profile.AccountHandler'),
    (r"/profile/edit", 'handlers.profile.EditHandler'),
    (r"/profile/verify", 'handlers.profile.VerifyHandler'),
    (r"/profile/follow/([A-Za-z0-9]+)", 'handlers.profile.FollowHandler'),
    (r"/profile/followers/([A-Za-z0-9]+)", 'handlers.profile.FollowersHandler'),
    (r"/profile/donations", 'handlers.donation.ListHandler'),
    (r"/profile/comments", 'handlers.profile.CommentsHandler'),
    (r"/profile/comments/([A-Za-z0-9]+)", 'handlers.profile.ProfileCommentsHandler'),
    (r"/profile/articles/([A-Za-z0-9]+)", 'handlers.profile.ArticlesHandler'),
    (r"/profile/activities/([A-Za-z0-9]+)", 'handlers.profile.ActivitiesHandler'),
    (r"/profile/([A-Za-z0-9]+)", 'handlers.profile.ViewHandler'),

    (r"/register", 'handlers.auth.RegisterHandler'),
    (r"/new-user", 'handlers.auth.NewUserHandler'),
    (r"/dashboard", 'handlers.profile.Dashboard'),

    (r"/activities", 'handlers.activity.ListHandler'),
    (r"/activity/new", 'handlers.activity.EditHandler'),
    (r"/activity/edit/([A-Za-z0-9\-]+)", 'handlers.activity.EditHandler'),
    (r"/activity/edit", 'handlers.activity.EditHandler'),
    (r"/activity/remove/([A-Za-z0-9\-]+)", 'handlers.activity.RemoveHandler'),
    (r"/activity/([A-Za-z0-9\-]+)", 'handlers.activity.ViewHandler'),

    (r"/articles", 'handlers.article.ListHandler'),
    (r"/article/new", 'handlers.article.EditHandler'),
    (r"/article/edit/([A-Za-z0-9\-]+)", 'handlers.article.EditHandler'),
    (r"/article/edit", 'handlers.article.EditHandler'),
    (r"/article/remove/([A-Za-z0-9\-]+)", 'handlers.article.RemoveHandler'),
    (r"/article/([A-Za-z0-9\-]+)", 'handlers.article.ViewHandler'),

    (r"/page/new", 'handlers.page.EditHandler'),
    (r"/page/edit/([A-Za-z0-9\-]+)", 'handlers.page.EditHandler'),
    (r"/page/edit", 'handlers.page.EditHandler'),
    (r"/page/([A-Za-z0-9\-]+)", 'handlers.page.ViewHandler'),

    (r"/users", 'handlers.profile.UserListHandler'),

    (r"/tag/([a-z0-9]+)", 'handlers.tag.ViewHandler'),
    (r"/tags", 'handlers.tag.ListHandler'),
    (r"/flag", 'handlers.tag.FlagHandler'),

    (r"/report", 'handlers.report.Handler'),

    (r"/login/fb", 'handlers.auth.FacebookLoginHandler'),
    (r"/login/google", 'handlers.auth.GoogleLoginHandler'),
    (r"/login/twitter", 'handlers.auth.TwitterLoginHandler'),
    (r"/login/yahoo", 'handlers.auth.YahooLoginHandler'),
    (r"/login", 'handlers.auth.LoginFormHandler'),
    (r"/logout.*", 'handlers.auth.LogoutHandler'),
]
