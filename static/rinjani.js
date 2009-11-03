function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var Rinjani = {
	/* flash container enhanced? */
  _flash_container_enhanced : false,

	/* return the flash container */
  getFlashContainer : function(nocreate) {
    var container = $('#flash_message');
    if (container.length == 0) {
      if (nocreate)
        return null;
      container = $('<div id="flash_message"></div>').prependTo('div.main').hide();
    }
    if (!Rinjani._flash_container_enhanced) {
      Rinjani._flash_container_enhanced = true;
      container.prepend($('<div class="close"><a href="#"><span>[x]</span></a>')
        .bind('click', function() {
          container.fadeOut('slow', function() {
            $('p', container).remove();
          });
          return false;
        }));
    }
    return container;
  },

  /* fade in the flash message */
  fadeInFlashMessages : function() {
    var container = Rinjani.getFlashContainer(true);
    if (container && !container.is(':visible'))
      container.animate({
        height:   'show',
        opacity:  'show'
      }, 'fast');
  },
  
  /* flashes a message from javascript */
  flash : function(text) {
    var container = Rinjani.getFlashContainer();
    $('<p>').text(text).appendTo(container);
    Rinjani.fadeInFlashMessages();
  },
  
  /* make selects with the correct class submit forms on select */
  submitOnSelect : function(element) {
    $('select', element).bind('change', function() {
      this.form.submit();
    });
  },
  
  /* Parse an iso8601 date into a date object */
  parseISO8601 : function(string) {
    return new Date(string
      .replace(/(?:Z|([+-])(\d{2}):(\d{2}))$/, ' GMT$1$2$3')
      .replace(/^(\d{4})-(\d{2})-(\d{2})T?/, '$1/$2/$3 ')
    );
  },
  
  /* fades in errors */
  highlightErrors : function(element) { 
    var errors = $('ul.errors', element).hide().fadeIn();
  },
  
  addTag: function(tag, el) {
		tag_el = el || $('input[name=tags]').get(0);
        var value = tag_el.value;
        var usedTags = new Array;
        if (value.length) {
            usedTags = value.split(/\s*\,\s*/);
        }
        tag = tag.replace(new RegExp('(__SINGLE_QUOTE__)', 'g'), "'");
        for (var i in usedTags) {
            if (usedTags[i] == tag) {
		if (!el) alert('' + tag + ' is already in the list.  To remove a tag, edit the field above.');
		return;
           }
        }
        usedTags.push(tag);
        tag_el.value = usedTags.join(', ');
        tag_el.focus(1);
	},
	
	setupDropdownMenu: function() {
		$(".dd_menu img.arrow").hover(function(){
	        $(".head_menu").removeClass('active');
	        submenu = $(this).parent().parent().find(".sub_menu");
	        if(submenu.css('display')=="block") {
	            $(this).parent().removeClass("active");
	            submenu.hide();
	            $(this).attr('src','/static/css/img/arrow_hover.png');
	        }else {
	            $(this).parent().addClass("active");
	            submenu.fadeIn();
	            $(this).attr('src','/static/css/img/arrow_select.png');
	        }
	        $(".sub_menu:visible").not(submenu).hide();
	        $(".dd_menu img.arrow").not(this).attr('src','/static/css/img/arrow.png');
	    })
	    .mouseover(function(){
	        $(this).attr('src','/static/css/img/arrow_hover.png');
	    })
	    .mouseout(function(){
	        if($(this).parent().parent().find("div.sub_menu").css('display')!="block"){
	            $(this).attr('src','/static/css/img/arrow.png');
	        }else{
	            $(this).attr('src','/static/css/img/arrow_select.png');
	        }
	    });
	    
	    $(".dd_menu .head_menu").mouseover(function(){ $(this).addClass('over'); })
	    .mouseout(function(){ $(this).removeClass('over'); });
	    
	    $(".dd_menu .sub_menu").mouseover(function(){ $(this).fadeIn(); })
	    .blur(function(){
	        $(this).hide();
	        $(".head_menu").removeClass('active');
	    });
	    
	    $(document).click(function(event){
	        var target = $(event.target);
	        if (target.parents(".dd_menu").length == 0) {
	            $(".dd_menu .head_menu").removeClass('active');
	            $(".dd_menu .sub_menu").hide();
	            $(".dd_menu img.arrow").attr('src','/static/css/img/arrow.png');
	        }
	    });
	},
	
	insertAtCaret: function (target, s) {
		// mod from http://www.mail-archive.com/jquery-en@googlegroups.com/msg08708.html
		t = $(target).get(0);
	    //IE support
	    if (document.selection) {
	        t.focus();
	        sel = document.selection.createRange();
	        sel.text = s;
	        t.focus();
	    }
	    //MOZILLA/NETSCAPE support
	    else if (this.selectionStart || this.selectionStart == '0') {
	        var startPos = this.selectionStart;
	        var endPos = this.selectionEnd;
	        var scrollTop = this.scrollTop;
	        t.value = t.value.substring(0, startPos)
	              + s
	              + t.value.substring(endPos, t.value.length);
	        t.focus();
	        t.selectionStart = startPos + s.length;
	        t.selectionEnd = startPos + s.length;
	        t.scrollTop = scrollTop;
	    } else {
	        t.value += s;
	        t.focus();
	    }
	}
};

$.fn.attachments = function(options) {
	var opts = $.extend($.fn.attachments.defaults, options);
    opts.parser = opts.parser? opts.parser : $.fn.attachments.fieldParser;
    if (!opts.template) return; 

	return this.filter(':input').each(function() {
        if ($(this).val() == '') return;
		var s = $(this).val().split(opts.separator);
        
	    attachments = [];
	    if (s.length) {               
	        $.each(s, function(i, val) {
	            val = val.split(opts.field_separator);
	            attachment = opts.parser(val);
	            attachments.push(attachment);
	        });
	    }
	    $.each(attachments, function(i, val) {
	    	$(opts.target).append(opts.template, val);
	    });
	});
};

$.fn.attachments.fieldParser = function(val) {
    return {no: val[0], src: val[1], title: val[2]};
};

$.fn.attachments.defaults = { 
  template: null,
  target: '.attachments',
  separator: '$',
  field_separator: '#',
  parser: null
};

if ($.fn.template) {
	var attachmentTemplate = $.template("<div class='thumb tt' title='${title}'><a href='#' onclick='R.insertAtCaret(\"#content\", \"{{attachment ${no} caption=\\\"Edit the caption\\\"}}\n\")'><img title='Click to insert ${title}' src='${src}' /><span>${no}</span></a></div>");
	$.fn.attachments.defaults.template = attachmentTemplate;
}

var R = Rinjani;

$(function() {
	R.fadeInFlashMessages();
    R.setupDropdownMenu();
    
	$('#hsearch input[type=text]').each(function() {
        var hint = $(this).val();
        $(this).val(hint).click(function() { $(this).val(""); }).blur(function() { $(this).val(hint); });
    });

    // the ajax setup
    $.ajaxSetup({
        error: function() {
        Rinjani.flash('Could not contact server. Connection problems?');
        }
    });
    
    var dialog = $("a.dialog[rel]").overlay({ 
        expose: { 
            color: '#000', 
            loadSpeed: 100, 
            opacity: 0.3
        }, 
        effect: 'apple', 
        closeOnClick: false,
        onBeforeLoad: function() { 
            // grab wrapper element inside content 
            var wrap = this.getContent().find(".contentWrapper"); 
            // load the page specified in the trigger 
            wrap.load(this.getTrigger().attr("href")); 
        } 
    }); 
    
    // select all desired input fields and attach tooltips to them 
	$("form.withtips :input[title], .tt").tooltip({ 
	    position: "center right", 
	    offset: [0,-10], 
	    effect: "fade", 
	    tip: '.tooltip' 
	});
	
	// setup rich text editor
	if ($.markItUp) {
	    mySettings = $.extend(mySettings || {}, {
	        previewParserPath: window.BP + '/preview',
	        previewPosition: 'after',
	        previewAutoRefresh: false
	        //previewInWindow: 'width=600, height=300, resizable=yes, scrollbars=yes'
	    });
	    $('.rte').markItUp(mySettings);
	    $('.rte').each(function() {
	    	$(this).css('height', $(this).attr('rows') + 'em');
	    });
	}
	
    $("ul.tabs").tabs("div.panes > div"); 
    
});
