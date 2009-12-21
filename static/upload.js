
/*
 * apit: attachments data stored as $.data or el metadata will be much simpler?
 */

$.fn.attachments = function(options) {
    var opts = $.extend($.fn.attachments.defaults, options);
    if (!opts.template) return;
    var template = $.template(opts.template);

    opts.parser = opts.parser? opts.parser : $.fn.attachments.fieldParser;

    return this.filter(':input').each(function() {
        if ($(this).val() == '') return;
        attachments = $.fn.attachments.parseAttachments($(this).val(), opts);
        $.each(attachments, function(i, val) {
            $(opts.target).append(template, val);
        });
    });
};
// cache
$.fn.attachments._attachments = null;

$.fn.attachments.parseAttachments = function(s, o) {
    var s = s.split(o.separator);
    if (s.length) {
        attachments = [];
        $.each(s, function(i, val) {
            val = val.split(o.field_separator);
            attachment = o.parser(val);
            attachments.push(attachment);
        });
        $.fn.attachments._attachments = attachments;
        return attachments;
    }
};

$.fn.attachments.fieldParser = function(val) {
    // (type, src=src, thumb_src=thumb_src, filename=a[4])
    // doh, ini gmn mimetype supaya bs masuk setting ya
    var src = "/static/img/attachment.png";
    if (val[1] != 'application/pdf') {
        src = "/static/uploads/" + val[2];
    }
    return {type: val[0], id: val[3], src: src, title: val[3]};
};

$.fn.attachments.defaults = {
    template: null,
    textarea: '#content',
    default_caption: 'Change Me',
    target: '.attachments',
    separator: '$',
    field_separator: '#',
    parser: null
};

$(function() {
    settings = {
        action: '/attachment/add',
        name: 'doc',
        responseType: 'json',
        errorInvalidType: "Please upload only photo or PDF file",
        data: {
            _xsrf: $.cookie('_xsrf'),
            type: content_type,
            is_new_doc: is_new_doc,
            slug: slug,
            name: 'doc'
        },
        onSubmit: function(file , ext){
            if (!ext || !/^(jpg|png|jpeg|gif|pdf)$/.test(ext)){
                alert(this._settings.errorInvalidType);
                return false;
            }
            settings.data.attachments = $attachments.val();
            settings.data.attachment_counter = $counter.val();
            $('#loading').show();
            this.disable();
        },
        onComplete: function(file, res) {
            if (res.status == 'OK') {
                   $('.attachments').append($(res.data.html));
                   $attachments.val(res.data.attachments);
                   $counter.val(res.data.counter);
            } else {
                //R.flash("Uploading failed. Please contact administrator");
                R.flash(res.message);
            }
            $('#loading').hide();
            this.enable();
        }
    };

    new AjaxUpload('#upload-button', settings);

    var tt =
        "<div class='thumb'>" +
            "<img rel='${type}' src='${src}' />" +
            "<span class='insert' rel='${id}' title='Click to insert'>^</span>" +
            "<span class='rm' rel='${id}' title='Click to remove'>X</span>" +
        "</div>";

    $attachments.attachments({template: tt, textarea: textarea});

    $('.thumb .rm').live('click', function() {
        if (!confirm('This will delete the file. Are you sure?')) return;
        filename = $(this).attr('rel');
        $thumb = $(this).parents('.thumb');
        opts = $.fn.attachments.defaults;
        attachment_type = $('img', $thumb).attr('rel');
        R.request('/attachment/remove',
                {filename: filename, type:content_type,
                    attachment_type: attachment_type, slug:slug,
                    thumb: $thumb.find('img').attr('src')
                },
                'post',
                function(resp) {
                    attachments = $attachments.val().split(opts.separator);
                    _attachments = [];
                    $.each(attachments, function(i, val) {
                        a = val.split(opts.field_separator);
                        if (a[3] != filename) {
                            _attachments.push(val);
                        }
                    });

                    $attachments.val(_attachments.join(opts.separator));
                    $counter.val(Math.max(parseInt($counter.val()) - 1, 0));
                    $thumb.remove();
                    alert("Please remove reference to " + filename + " attachment in your content.");
                }
        );
    });
    $('.thumb .insert').live('click', function() {
        filename = $(this).attr('rel');
        opts = $.fn.attachments.defaults;
        txt = "\n{{ attachment " + filename + " caption='" + opts.default_caption + "'}}\n";
        R.insertAtCaret(opts.textarea, txt);
    });
});
