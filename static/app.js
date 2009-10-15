function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax(
        {
            url: url, 
            data: $.param(args), 
            dataType: "json", 
            type: "POST",
            success: function(response) {
                //callback(eval("(" + response + ")"));
                alert('ok')
            }
        });
};

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
  }


}


$(function() {
    /* the ajax setup */
    $.ajaxSetup({
        error: function() {
        Rinjain.flash(_('Could not contact server. Connection problems?'));
        }
    });
  
    /* flash messages get a close button and are nicely faded in */
    Rinjani.fadeInFlashMessages();
  
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
    
    $(".dd_menu .head_menu").mouseover(function(){ $(this).addClass('over') })
    .mouseout(function(){ $(this).removeClass('over') });
    
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


});
