// see models.py
CONTENT_TYPE = {
    GENERIC: 1,
    ARTICLE: 2,
    ACTIVITY: 3,
    PAGE: 4
}

TAGS = ['economy', 'education', 'enterpreneurship', 'training', 'inspiring', 'public-figure', 'interview', 'photo', 'failure']
USERTAGS = ['enterpreneurship', 'social-media', 'healtcare', 'ICT', 'insurance']

EXCERPT = [
    'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Integer risus velit, facilisis eget, viverra et, venenatis id.',
    'Quisque dictum quam vel neque. Aenean justo ipsum, luctus ut, volutpat laoreet, vehicula in, libero.',
    'Donec tempus quam quis neque. Quisque malesuada nulla sed pede volutpat pulvinar. Integer porta. Morbi urna. Etiam pede nunc, vestibulum vel.',
    ' Nulla sagittis condimentum ligula. Curabitur lorem risus, sagittis vitae, accumsan a, iaculis id, metus. In consectetuer, lorem eu lobortis egestas, velit odio imperdiet eros',
    'Pellentesque viverra dolor non nunc. Praesent lacus. Sed non ipsum. Donec ut purus. Aliquam sed erat.'
]

Article = {
    template : {
        type: CONTENT_TYPE.ARTICLE,
        status: 'published',
        featured: false, enable_comment: false, comment_count: 0, view_count: 0,
        tags: [], votes: {}, attachments: [],
        content: "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Integer risus velit, facilisis eget, viverra et, venenatis id, leo. Donec nonummy lacinia leo. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Pellentesque tempor. Donec rutrum venenatis dui. Praesent a eros. Nam pharetra. Phasellus magna sem, vulputate eget, ornare sed, dignissim sit amet, pede. Nunc metus. Curabitur lorem risus, sagittis vitae, accumsan a, iaculis id, metus.  \n\nDonec tempus quam quis neque. Quisque malesuada nulla sed pede volutpat pulvinar. Integer porta. Morbi urna. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Etiam cursus purus interdum libero. Morbi turpis arcu, egestas congue, condimentum quis, tristique cursus, leo. Suspendisse viverra placerat tortor. Suspendisse fermentum. Quisque facilisis, urna sit amet pulvinar mollis, purus arcu adipiscing velit, non condimentum diam purus eu massa. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Vivamus nisi elit, nonummy id, facilisis non, blandit ac, dolor. \n\nIn hac habitasse platea dictumst. Aliquam imperdiet lobortis metus. Integer tempus malesuada pede. Quisque malesuada nulla sed pede volutpat pulvinar. Phasellus nisi metus, tempus sit amet, ultrices ac, porta nec, felis. Vivamus quis mi. Etiam pharetra lacus sed velit imperdiet bibendum. Pellentesque viverra dolor non nunc. Suspendisse potenti. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec gravida, ante vel ornare lacinia, orci enim porta est, eget sollicitudin lectus lectus eget lacus. Mauris et dolor. Ut venenatis. Sed dolor. Sed quis elit. Curabitur nunc ante, ullamcorper vel, auctor a, aliquam at, tortor. Nullam venenatis gravida orci. Quisque dictum quam vel neque. Aenean justo ipsum, luctus ut, volutpat laoreet, vehicula in, libero. Nam nisl quam, posuere non, volutpat sed, semper vitae, magna. \n\nDonec at diam a tellus dignissim vestibulum. Quisque arcu ante, cursus in, ornare quis, viverra ut, justo. Maecenas viverra. Praesent a eros. In hac habitasse platea dictumst. Vestibulum viverra varius enim. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aliquam vel nibh. Mauris tincidunt aliquam ante. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Phasellus auctor enim eget sem. Pellentesque viverra dolor non nunc. Praesent lacus. Sed non ipsum. Donec ut purus. Aliquam sed erat.",
        content_html: "<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Integer risus velit, facilisis eget, viverra et, venenatis id, leo. Donec nonummy lacinia leo. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Pellentesque tempor. Donec rutrum venenatis dui. Praesent a eros. Nam pharetra. Phasellus magna sem, vulputate eget, ornare sed, dignissim sit amet, pede. Nunc metus. Curabitur lorem risus, sagittis vitae, accumsan a, iaculis id, metus.  <br /><br />Donec tempus quam quis neque. Quisque malesuada nulla sed pede volutpat pulvinar. Integer porta. Morbi urna. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Etiam cursus purus interdum libero. Morbi turpis arcu, egestas congue, condimentum quis, tristique cursus, leo. Suspendisse viverra placerat tortor. Suspendisse fermentum. Quisque facilisis, urna sit amet pulvinar mollis, purus arcu adipiscing velit, non condimentum diam purus eu massa. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Vivamus nisi elit, nonummy id, facilisis non, blandit ac, dolor. <br /><br />In hac habitasse platea dictumst. Aliquam imperdiet lobortis metus. Integer tempus malesuada pede. Quisque malesuada nulla sed pede volutpat pulvinar. Phasellus nisi metus, tempus sit amet, ultrices ac, porta nec, felis. Vivamus quis mi. Etiam pharetra lacus sed velit imperdiet bibendum. Pellentesque viverra dolor non nunc. Suspendisse potenti. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec gravida, ante vel ornare lacinia, orci enim porta est, eget sollicitudin lectus lectus eget lacus. Mauris et dolor. Ut venenatis. Sed dolor. Sed quis elit. Curabitur nunc ante, ullamcorper vel, auctor a, aliquam at, tortor. Nullam venenatis gravida orci. Quisque dictum quam vel neque. Aenean justo ipsum, luctus ut, volutpat laoreet, vehicula in, libero. Nam nisl quam, posuere non, volutpat sed, semper vitae, magna. <br /><br />Donec at diam a tellus dignissim vestibulum. Quisque arcu ante, cursus in, ornare quis, viverra ut, justo. Maecenas viverra. Praesent a eros. In hac habitasse platea dictumst. Vestibulum viverra varius enim. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aliquam vel nibh. Mauris tincidunt aliquam ante. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Phasellus auctor enim eget sem. Pellentesque viverra dolor non nunc. Praesent lacus. Sed non ipsum. Donec ut purus. Aliquam sed erat.</p>",
    },
    type: 'Article',
    counter: 'article_count',
    collectionName: 'contents'
}

Activity = {
    template : {
        type: CONTENT_TYPE.ACTIVITY,
        status: 'published',
        featured: false, enable_comment: false, comment_count: 0, view_count: 0,
        tags: [], votes: {}, attachments: [], lat: null, lang: null,
        date_start: null, date_end: null, location: {}, state: 'running', validated_by: [],
        need_volunteer: false, volunteer_tags: [], need_donation: true, donation_amount_needed: 1000, donation_amount: 0,
        content: "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Integer risus velit, facilisis eget, viverra et, venenatis id, leo. Donec nonummy lacinia leo. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Pellentesque tempor. Donec rutrum venenatis dui. Praesent a eros. Nam pharetra. Phasellus magna sem, vulputate eget, ornare sed, dignissim sit amet, pede. Nunc metus. Curabitur lorem risus, sagittis vitae, accumsan a, iaculis id, metus.  \n\nDonec tempus quam quis neque. Quisque malesuada nulla sed pede volutpat pulvinar. Integer porta. Morbi urna. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Etiam cursus purus interdum libero. Morbi turpis arcu, egestas congue, condimentum quis, tristique cursus, leo. Suspendisse viverra placerat tortor. Suspendisse fermentum. Quisque facilisis, urna sit amet pulvinar mollis, purus arcu adipiscing velit, non condimentum diam purus eu massa. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Vivamus nisi elit, nonummy id, facilisis non, blandit ac, dolor. \n\nIn hac habitasse platea dictumst. Aliquam imperdiet lobortis metus. Integer tempus malesuada pede. Quisque malesuada nulla sed pede volutpat pulvinar. Phasellus nisi metus, tempus sit amet, ultrices ac, porta nec, felis. Vivamus quis mi. Etiam pharetra lacus sed velit imperdiet bibendum. Pellentesque viverra dolor non nunc. Suspendisse potenti. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec gravida, ante vel ornare lacinia, orci enim porta est, eget sollicitudin lectus lectus eget lacus. Mauris et dolor. Ut venenatis. Sed dolor. Sed quis elit. Curabitur nunc ante, ullamcorper vel, auctor a, aliquam at, tortor. Nullam venenatis gravida orci. Quisque dictum quam vel neque. Aenean justo ipsum, luctus ut, volutpat laoreet, vehicula in, libero. Nam nisl quam, posuere non, volutpat sed, semper vitae, magna. \n\nDonec at diam a tellus dignissim vestibulum. Quisque arcu ante, cursus in, ornare quis, viverra ut, justo. Maecenas viverra. Praesent a eros. In hac habitasse platea dictumst. Vestibulum viverra varius enim. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aliquam vel nibh. Mauris tincidunt aliquam ante. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Phasellus auctor enim eget sem. Pellentesque viverra dolor non nunc. Praesent lacus. Sed non ipsum. Donec ut purus. Aliquam sed erat.",
        content_html: "<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Integer risus velit, facilisis eget, viverra et, venenatis id, leo. Donec nonummy lacinia leo. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Pellentesque tempor. Donec rutrum venenatis dui. Praesent a eros. Nam pharetra. Phasellus magna sem, vulputate eget, ornare sed, dignissim sit amet, pede. Nunc metus. Curabitur lorem risus, sagittis vitae, accumsan a, iaculis id, metus.  <br /><br />Donec tempus quam quis neque. Quisque malesuada nulla sed pede volutpat pulvinar. Integer porta. Morbi urna. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Etiam cursus purus interdum libero. Morbi turpis arcu, egestas congue, condimentum quis, tristique cursus, leo. Suspendisse viverra placerat tortor. Suspendisse fermentum. Quisque facilisis, urna sit amet pulvinar mollis, purus arcu adipiscing velit, non condimentum diam purus eu massa. Etiam pede nunc, vestibulum vel, rutrum et, tincidunt eu, enim. Vivamus nisi elit, nonummy id, facilisis non, blandit ac, dolor. <br /><br />In hac habitasse platea dictumst. Aliquam imperdiet lobortis metus. Integer tempus malesuada pede. Quisque malesuada nulla sed pede volutpat pulvinar. Phasellus nisi metus, tempus sit amet, ultrices ac, porta nec, felis. Vivamus quis mi. Etiam pharetra lacus sed velit imperdiet bibendum. Pellentesque viverra dolor non nunc. Suspendisse potenti. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec gravida, ante vel ornare lacinia, orci enim porta est, eget sollicitudin lectus lectus eget lacus. Mauris et dolor. Ut venenatis. Sed dolor. Sed quis elit. Curabitur nunc ante, ullamcorper vel, auctor a, aliquam at, tortor. Nullam venenatis gravida orci. Quisque dictum quam vel neque. Aenean justo ipsum, luctus ut, volutpat laoreet, vehicula in, libero. Nam nisl quam, posuere non, volutpat sed, semper vitae, magna. <br /><br />Donec at diam a tellus dignissim vestibulum. Quisque arcu ante, cursus in, ornare quis, viverra ut, justo. Maecenas viverra. Praesent a eros. In hac habitasse platea dictumst. Vestibulum viverra varius enim. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aliquam vel nibh. Mauris tincidunt aliquam ante. Vivamus posuere, ante eu tempor dictum, felis nibh facilisis sem, eu auctor metus nulla non lorem. Aenean turpis ipsum, rhoncus vitae, posuere vitae, euismod sed, ligula. Phasellus auctor enim eget sem. Pellentesque viverra dolor non nunc. Praesent lacus. Sed non ipsum. Donec ut purus. Aliquam sed erat.</p>",
    },
    type: 'Activity',
    counter: 'activity_count',
    collectionName: 'contents'
}

function removeArrDuplicate(a) {
    a.sort();
    for (var i = 1; i < a.length; i++) {
        if (a[i-1] == a[i]) {
            a.splice(i, 1);
            i--;
        }
    }
}

var choose_tags = function(T) {
	if (Math.floor(Math.random()) == 4) 
    	return []
    	        
    if (!T) { T = TAGS; }
    tags = [];
    for(var i=Math.floor(Math.random() * 5); i>=0; i--) {
        tags[i] = T[Math.floor(Math.random() * T.length)];
    }
    removeArrDuplicate(tags);
    return tags;
}

var choose_date = function(offset) {
    d = new Date();
    d.setTime(d.getTime() - offset * 60*60*3*1000); // 3 hours
    return d;
}

var choose_excerpt = function() {
    return EXCERPT[Math.floor(Math.random() * EXCERPT.length)];
}

var generate_random_content = function(ctype, id) {
    uid = "User-" + (1 + Math.floor(Math.random() * 50));
    t = ctype.template;
    t["_id"] = ctype.type + "-" + id;
    t["title"] = ctype.type + " #" + id;
    t["slug"] = ctype.type.toLowerCase() + "-" + id;
    t["author"] = new DBRef("users", uid);
    t['excerpt'] = choose_excerpt();
    t["created_at"] = choose_date(id);
    t["updated_at"] = t['created_at'];
    t["view_count"] = 1 + Math.floor(Math.random() * 500)
    t['tags'] = choose_tags();
    db[ctype.collectionName].save(t);

    assert( db.getPrevError().err == null , db.getPrevError().err );

    u = db.users.findOne({_id: uid});
    if (u) {
        u[ctype.counter] += 1;
        db.users.save(u);
    }

}

ut = { _required_namespace: [], document_scan : null, last_login: new Date(), "website" : null, "profile_content_html" : null, "uid" : null, "locale" : null, "phones" : [], "auth_provider" : "form", "sex" : null, "birthday_date" : null, "timezone" : "Asia/Jakarta", "badges" : [], "attachments" : [], "preferences" : [], "article_count" : 0, "location" : [], "followers" : [], "is_verified" : true, "email" : null, "fax" : [], "tags" : [], "activity_count" : 0, "following" : [], "password_hashed" : "a7257ef242a856304478236fe46fee00f23f8a25", "is_admin" : false, "address" : null, "profile_content" : null, "fullname" : null, "access_token" : null, "type" : "agent", "points" : 0, "status" : "active", "avatar" : null, "donation_count" : 0, "contact_person" : null }
for(var id=1; id < 51; id++) {
    ut["_id"] = "User-" + id;
    ut["username"] = "user" + id;
    ut["about"] = "About mee user-" + id;
    ut['tags'] = choose_tags(USERTAGS);
    ut["created_at"] = choose_date(id);
    ut["updated_at"] = ut['created_at'];
    db.users.save(ut);
}

[Article, Activity].forEach(function(ctype) {
    for (var id=1; id<250; id++) {
        generate_random_content(ctype, id);
    }
});

print("User size: " + db.users.totalSize());
print("Content size: " + db.contents.totalSize());
