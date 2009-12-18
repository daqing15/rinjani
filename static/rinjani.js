
/* metadata plugin
 * Copyright (c) 2006 John Resig, Yehuda Katz, Jörn Zaefferer, Paul McLanahan*/
(function($){$.extend({metadata:{defaults:{type:"class",name:"metadata",cre:/({.*})/,single:"metadata"},setType:function(type,name){this.defaults.type=type;this.defaults.name=name},get:function(elem,opts){var settings=$.extend({},this.defaults,opts);if(!settings.single.length){settings.single="metadata"}var data=$.data(elem,settings.single);if(data){return data}data="{}";if(settings.type=="class"){var m=settings.cre.exec(elem.className);if(m){data=m[1]}}else{if(settings.type=="elem"){if(!elem.getElementsByTagName){return undefined}var e=elem.getElementsByTagName(settings.name);if(e.length){data=$.trim(e[0].innerHTML)}}else{if(elem.getAttribute!=undefined){var attr=elem.getAttribute(settings.name);if(attr){data=attr}}}}if(data.indexOf("{")<0){data="{"+data+"}"}data=eval("("+data+")");$.data(elem,settings.single,data);return data}}});$.fn.metadata=function(opts){return $.metadata.get(this[0],opts)}})(jQuery);

/* http://tympanus.net/jMaxInput/ (c) cody */
(function(a){a.fn.maxinput=function(b){var c=a.extend({},a.fn.maxinput.defaults,b);return this.each(function(){$this=a(this);var d=a.meta?a.extend({},c,$this.data()):c;a.fn.limit(d,$this)})};a.fn.maxinput.defaults={limit:140,position:"after",showtext:true,message:"characters left"};a.fn.limit=function(e,d){var c=d.parents("form");if(!a(".jmaxtext",c).length){var g=a(document.createElement("div")).addClass("jmaxtext grey small");g.html("<span>"+e.limit+"</span>");if(e.position=="after"){d.after(g)}else{d.before(g)}}var b=d.val().length;a(".jmaxtext span:first",c).html(e.limit-b);if((b>0)&&(b<=e.limit)){a(":submit",c).removeAttr("disabled").removeClass("disabled").addClass("enabled")}else{a(":submit",c).attr("disabled","true").removeClass("enabled").addClass("disabled")}d.one("keydown",function(){var f=function(){d.maxinput(e)};timeout=setTimeout(f,1)})}})(jQuery);

/* cookie plugin - Copyright (c) 2006 Klaus Hartl (stilbuero.de) */
jQuery.cookie=function(name,value,options){if(typeof value!='undefined'){options=options||{};if(value===null){value='';options=$.extend({},options);options.expires=-1;}var expires='';if(options.expires&&(typeof options.expires=='number'||options.expires.toUTCString)){var date;if(typeof options.expires=='number'){date=new Date();date.setTime(date.getTime()+(options.expires*24*60*60*1000));}else{date=options.expires;}expires='; expires='+date.toUTCString();}var path=options.path?'; path='+(options.path):'';var domain=options.domain?'; domain='+(options.domain):'';var secure=options.secure?'; secure':'';document.cookie=[name,'=',encodeURIComponent(value),expires,path,domain,secure].join('');}else{var cookieValue=null;if(document.cookie&&document.cookie!=''){var cookies=document.cookie.split(';');for(var i=0;i<cookies.length;i++){var cookie=jQuery.trim(cookies[i]);if(cookie.substring(0,name.length+1)==(name+'=')){cookieValue=decodeURIComponent(cookie.substring(name.length+1));break;}}}return cookieValue;}};

/* Babel JavaScript Support
 * Copyright (C) 2008 Edgewall Software */
var babel=new function(){var b=function(d){return d==1?0:1};var c=/%?%(?:\(([^\)]+)\))?([disr])/g;var a=this.Translations=function(d,e){this.messages={};this.locale=d||"unknown";this.domain=e||"messages";this.pluralexpr=b};a.load=function(d){var e=new a();e.load(d);return e};a.prototype={gettext:function(d){var e=this.messages[d];if(typeof e=="undefined"){return d}return(typeof e=="string")?e:e[0]},ngettext:function(e,d,g){var f=this.messages[e];if(typeof f=="undefined"){return(g==1)?e:d}return f[this.pluralexpr(g)]},install:function(){var d=this;window._=window.gettext=function(e){return d.gettext(e)};window.ngettext=function(f,e,g){return d.ngettext(f,e,g)};return this},load:function(d){if(d.messages){this.update(d.messages)}if(d.plural_expr){this.setPluralExpr(d.plural_expr)}if(d.locale){this.locale=d.locale}if(d.domain){this.domain=d.domain}return this},update:function(d){for(var e in d){if(d.hasOwnProperty(e)){this.messages[e]=d[e]}}return this},setPluralExpr:function(d){this.pluralexpr=new Function("n","return +("+d+")");return this}};this.format=function(){var e,f=arguments[0],d=0;if(arguments.length==1){return f}else{if(arguments.length==2&&typeof arguments[1]=="object"){e=arguments[1]}else{e=[];for(var g=1,h=arguments.length;g!=h;++g){e[g-1]=arguments[g]}}}return f.replace(c,function(k,i,j){if(k[0]==k[1]){return k.substring(1)}var l=e[i||d++];return(j=="i"||j=="d")?+l:l})}};

/* jquery template (c) who? */
(function($){$.template=function(html,options){return new $.template.instance(html,options)};$.template.instance=function(html,options){if(options&&options.regx){options.regx=this.regx[options.regx]}this.options=$.extend({compile:false,regx:this.regx.standard},options||{});this.html=html;if(this.options.compile){this.compile()}this.isTemplate=true};$.template.regx=$.template.instance.prototype.regx={jsp:/\$\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}/g,ext:/\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}/g,jtemplates:/\{\{([\w-]+)(?:\:([\w\.]*)(?:\((.*?)?\))?)?\}\}/g};$.template.regx.standard=$.template.regx.jsp;$.template.helpers=$.template.instance.prototype.helpers={substr:function(value,start,length){return String(value).substr(start,length)}};$.extend($.template.instance.prototype,{apply:function(values){if(this.options.compile){return this.compiled(values)}else{var tpl=this;var fm=this.helpers;var fn=function(m,name,format,args){if(format){if(format.substr(0,5)=="this."){return tpl.call(format.substr(5),values[name],values)}else{if(args){var re=/^\s*['"](.*)["']\s*$/;args=args.split(",");for(var i=0,len=args.length;i<len;i++){args[i]=args[i].replace(re,"$1")}args=[values[name]].concat(args)}else{args=[values[name]]}return fm[format].apply(fm,args)}}else{return values[name]!==undefined?values[name]:""}};return this.html.replace(this.options.regx,fn)}},compile:function(){var sep=$.browser.mozilla?"+":",";var fm=this.helpers;var fn=function(m,name,format,args){if(format){args=args?","+args:"";if(format.substr(0,5)!="this."){format="fm."+format+"("}else{format='this.call("'+format.substr(5)+'", ';args=", values"}}else{args="";format="(values['"+name+"'] == undefined ? '' : "}return"'"+sep+format+"values['"+name+"']"+args+")"+sep+"'"};var body;if($.browser.mozilla){body="this.compiled = function(values){ return '"+this.html.replace(/\\/g,"\\\\").replace(/(\r\n|\n)/g,"\\n").replace(/'/g,"\\'").replace(this.options.regx,fn)+"';};"}else{body=["this.compiled = function(values){ return ['"];body.push(this.html.replace(/\\/g,"\\\\").replace(/(\r\n|\n)/g,"\\n").replace(/'/g,"\\'").replace(this.options.regx,fn));body.push("'].join('');};");body=body.join("")}eval(body);return this}});var $_old={domManip:$.fn.domManip,text:$.fn.text,html:$.fn.html};$.fn.domManip=function(args,table,reverse,callback){if(args[0].isTemplate){args[0]=args[0].apply(args[1]);delete args[1]}var r=$_old.domManip.apply(this,arguments);return r};$.fn.html=function(value,o){if(value&&value.isTemplate){var value=value.apply(o)}var r=$_old.html.apply(this,[value]);return r};$.fn.text=function(value,o){if(value&&value.isTemplate){var value=value.apply(o)}var r=$_old.text.apply(this,[value]);return r}})(jQuery);


jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
    json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

jQuery.fn.disable = function() {
    this.enable(false);
    return this;
};

jQuery.fn.enable = function(opt_enable) {
    if (arguments.length && !opt_enable) {
        this.attr("disabled", "disabled");
    } else {
        this.removeAttr("disabled");
    }
    return this;
};

var frameOnload = function(e) {
    if (e.contentDocument) {
        $(e).css('height', e.contentDocument.body.offsetHeight + 35);
    } else {
        $(e).css('height', e.contentWindow.document.body.scrollHeight)
    }
}

if (!window.console) window.console = {};
if (!window.console.log) window.console.log = function() {};

var Rinjani = {
  /* Solace. helper for dynamicSubmit and request */
  _standardRemoteCallback : function(func) {
      return function(resp) {
          if (typeof resp.try_login != 'undefined') {
              document.location.href = '/login-form?next='
                + encodeURIComponent(document.location.href);
               return;
          }
          if (func) func(resp);
          if (resp.message) { Rinjani.flash(resp.message); $.cookie('f', null); };
          if (resp.data && resp.data.next) {
              $.cookie('f', resp.data.msg);
              document.location=resp.data.next;
          }
          if (resp.data && resp.data.html_target) {
              $(resp.data.html_target).html(resp.data.html);
          }
        }
  },

  /* Solace. sends a request to a URL with optional data and
  evaluates the result.  You can only send requests
  to the own server that way and the endpoint has to
  return a valid json_response(). */
  request: function(url, data, method, callback) {
    data = $.extend({_xsrf:$.cookie('_xsrf')}, data);
    $.ajax({
      url:      url,
      type:     method || 'GET',
      data:     data,
      dataType: 'json',
      success:  Rinjani._standardRemoteCallback(callback)
    });
  },

  displayLoginForm: function() {

  },

    /* flash container enhanced? */
  _flash_container_enhanced : false,

    /* return the flash container */
  getFlashContainer : function(nocreate) {
    var container = $('#flashbar');
    if (container.length == 0) {
      if (nocreate)
        return null;
      container = $('<div id="flashbar"></div>').prependTo('div.main').hide();
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
    if (container && !container.is(':visible')) {
      container.animate({
        height:   'show',
        opacity:  'show'
      }, 'fast');
      timeout = setTimeout("Rinjani.getFlashContainer(false).slideUp();", 4000);
    }
  },

  /* flashes a message from javascript */
  flash : function(text,type) {
    clearTimeout(timeout);
    if (!type) type = 'I';
    var container = Rinjani.getFlashContainer();
    if (container.find('p').length) {
        container.find('p').text(text);
    } else {
        $('<p class="' + type + '">').text(text).appendTo(container);
    }
    Rinjani.fadeInFlashMessages();
  },

  /* make selects with the correct class submit forms on select */
  submitOnSelect : function(element) {
    $('select', element).bind('change', function() {
      this.form.submit();
    });
  },

    /* fades in errors */
    highlightErrors : function(element) {
        var errors = $('ul.errors', element).hide().fadeIn();
    },

    /* mod from multiply.com */
    addTag: function(tag, el) {
        if (el) {
            tag_el = $(el).get(0);
        } else {
            tag_el = $('input[name=tags]').get(0);
        }
        var value = tag_el.value;
        var usedTags = new Array;
        if (value.length) {
            usedTags = value.split(/\s*\,\s*/);
        }
        tag = tag.replace(new RegExp('(__SINGLE_QUOTE__)', 'g'), "'");
        for (var i in usedTags) {
            if (usedTags[i] == tag) {
                alert('' + tag + ' is already in the list.  To remove a tag, edit the field above.');
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
            }
            $(".sub_menu:visible").not(submenu).hide();
            $(".dd_menu img.arrow").not(this).attr('src','/static/css/img/arrow.png');
        })
        .mouseover(function(){
            $(this).attr('src','/static/css/img/arrow_hover.png');
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

    // mod from http://www.mail-archive.com/jquery-en@googlegroups.com/msg08708.html
    insertAtCaret: function (target, s) {
        t = $(target).get(0);
        //IE support
        if (document.selection) {
            t.focus();
            sel = document.selection.createRange();
            sel.text = s;
            t.focus();
        }
        //MOZILLA/NETSCAPE support
        else if (t.selectionStart || t.selectionStart == '0') {
            var startPos = t.selectionStart;
            var endPos = t.selectionEnd;
            var scrollTop = t.scrollTop;
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
    },

    setupAjax: function() {
      // the ajax setup
      $.ajaxSetup({
          error: function() {
              Rinjani.flash('Could not contact server. Connection problems?');
              $('#loading').hide();
          }
      });
      $('#loading').ajaxStart(function() {
            $(this).show();
      });
      $('#loading').ajaxStop(function() {
            $(this).hide();
      });
    },

    setupForm: function() {
        $('#hsearch input[type=text]').each(function() {
            var hint = $(this).val();
            $(this).val(hint).click(function() { $(this).val(""); }).blur(function() { $(this).val(hint); });
        });

        $('button.ajax').live('click', function() {
            var action=$(this).parent('form').attr('action');
            R.request(action, {}, 'POST');
            return false;
        });


        // setup rich text editor
        if ($.markItUp) {
            mySettings = $.extend(mySettings || {}, {
              previewAutoRefresh: true
            });
            $('.rte').markItUp(mySettings);
            $('li.preview a').trigger('mouseup');
            $('li.tPreview a').trigger('mouseup');
            $('.rte').each(function() {
                $(this).css('height', $(this).attr('rows') + 'em');
            });
            scroll(0,0);
        }

        $('.deps').each(function() {
              $src = $(this).find('.depsrc input[type=checkbox]');
              $src.click(function(i) {
                  $(this).parents('.deps').find('.deptarget').toggle();
              });
              if ($src.attr('checked')) {
                  $(this).find('.deptarget').show();
              }
          });

        $('.btn').each(function(){
            var b = $(this);
            var tt = b.text() || b.val();
            if ($(':submit,:button',this)) {
                b = $('<a>').insertAfter(this). addClass(this.className).attr('id',this.id);
                $(this).remove();
            }
            b.text('').css({cursor:'pointer'}). prepend('<i></i>').append($('<span>').
            text(tt).append('<i></i><span></span>'));
         });

    },
    setupUI: function() {
        Rinjani.setupDropdownMenu();

        // check if jQuery Tools exists
        if ($.fn.overlay) {
              var dialog = $(".dialog[rel]").overlay({
                  expose: '#000',
                  top: '25%',
                  closeOnClick: false,
                  onBeforeLoad: function() {
                      var wrap = this.getContent().find(".wDialog");
                      url = this.getTrigger().attr("href");
                      if (url != '#') {
                          wrap.load(url);
                      }
                  }
              });

              if ($('#slideshow').length) {
                  var slideshow = $(".slideshow a").overlay({
                    target: '#slideshow',
                    expose: '#000',
                    top: '25%',
                    closeOnClick: false,
                  })

                  if (slideshow.size()) {
                      slideshow.gallery({
                          speed: 800,
                          opacity:.6,
                          template: '<span>${index} of ${total}</span>'
                      });
                  }
              }

               // select all desired input fields and attach tooltips to them
              $("form.withtips :input[title], .tt").tooltip({
                  position: "center right",
                  offset: [-10,-5],
                  effect: "fade",
                  tip: '.tooltip'
              });

              $("ul.tabs").tabs("div.panes > div");
              $("ul.vtabs").tabs("div.vpanes > div");
          }
    }
};


var R = Rinjani;
var timeout;

$(function() {
    R.setupAjax();
    R.setupForm();
    R.setupUI();
    R.fadeInFlashMessages();
});

