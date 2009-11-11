/* jquery template (c) who? */
(function($){$.template=function(html,options){return new $.template.instance(html,options)};$.template.instance=function(html,options){if(options&&options.regx){options.regx=this.regx[options.regx]}this.options=$.extend({compile:false,regx:this.regx.standard},options||{});this.html=html;if(this.options.compile){this.compile()}this.isTemplate=true};$.template.regx=$.template.instance.prototype.regx={jsp:/\$\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}/g,ext:/\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}/g,jtemplates:/\{\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}\}/g};$.template.regx.standard=$.template.regx.jsp;$.template.helpers=$.template.instance.prototype.helpers={substr:function(value,start,length){return String(value).substr(start,length)}};$.extend($.template.instance.prototype,{apply:function(values){if(this.options.compile){return this.compiled(values)}else{var tpl=this;var fm=this.helpers;var fn=function(m,name,format,args){if(format){if(format.substr(0,5)=="this."){return tpl.call(format.substr(5),values[name],values)}else{if(args){var re=/^\s*['"](.*)["']\s*$/;args=args.split(",");for(var i=0,len=args.length;i<len;i++){args[i]=args[i].replace(re,"$1")}args=[values[name]].concat(args)}else{args=[values[name]]}return fm[format].apply(fm,args)}}else{return values[name]!==undefined?values[name]:""}};return this.html.replace(this.options.regx,fn)}},compile:function(){var sep=$.browser.mozilla?"+":",";var fm=this.helpers;var fn=function(m,name,format,args){if(format){args=args?","+args:"";if(format.substr(0,5)!="this."){format="fm."+format+"("}else{format='this.call("'+format.substr(5)+'", ';args=", values"}}else{args="";format="(values['"+name+"'] == undefined ? '' : "}return"'"+sep+format+"values['"+name+"']"+args+")"+sep+"'"};var body;if($.browser.mozilla){body="this.compiled = function(values){ return '"+this.html.replace(/\\/g,"\\\\").replace(/(\r\n|\n)/g,"\\n").replace(/'/g,"\\'").replace(this.options.regx,fn)+"';};"}else{body=["this.compiled = function(values){ return ['"];body.push(this.html.replace(/\\/g,"\\\\").replace(/(\r\n|\n)/g,"\\n").replace(/'/g,"\\'").replace(this.options.regx,fn));body.push("'].join('');};");body=body.join("")}eval(body);return this}});var $_old={domManip:$.fn.domManip,text:$.fn.text,html:$.fn.html};$.fn.domManip=function(args,table,reverse,callback){if(args[0].isTemplate){args[0]=args[0].apply(args[1]);delete args[1]}var r=$_old.domManip.apply(this,arguments);return r};$.fn.html=function(value,o){if(value&&value.isTemplate){var value=value.apply(o)}var r=$_old.html.apply(this,[value]);return r};$.fn.text=function(value,o){if(value&&value.isTemplate){var value=value.apply(o)}var r=$_old.text.apply(this,[value]);return r}})(jQuery);

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
        errorInvalidType: "Please select only photo or PDF file",
        data: {
            _xsrf: getCookie('_xsrf'),
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