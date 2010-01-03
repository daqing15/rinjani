/* jscrollpane - Copyright (c) 2009 Kelvin Luck (kelvin AT kelvinluck DOT com || http://www.kelvinluck.com) */
(function(a){a.jScrollPane={active:[]};a.fn.jScrollPane=function(c){c=a.extend({},a.fn.jScrollPane.defaults,c);var b=function(){return false};return this.each(function(){var t=a(this);var E=this;var am=0;var L;var an;var r;var ac=c.topCapHeight;if(a(this).parent().is(".jScrollPaneContainer")){am=c.maintainPosition?t.position().top:0;var q=a(this).parent();L=q.innerWidth();an=q.outerHeight();a(">.jScrollPaneTrack, >.jScrollArrowUp, >.jScrollArrowDown, >.jScrollCap",q).remove();t.css({top:0})}else{t.data("originalStyleTag",t.attr("style"));t.css("overflow","hidden");this.originalPadding=t.css("paddingTop")+" "+t.css("paddingRight")+" "+t.css("paddingBottom")+" "+t.css("paddingLeft");this.originalSidePaddingTotal=(parseInt(t.css("paddingLeft"))||0)+(parseInt(t.css("paddingRight"))||0);L=t.innerWidth();an=t.innerHeight();var j=a("<div></div>").attr({className:"jScrollPaneContainer"}).css({height:an+"px",width:L+"px"});if(c.enableKeyboardNavigation){j.attr("tabindex",c.tabIndex)}t.wrap(j);a(document).bind("emchange",function(ao,ap,p){t.jScrollPane(c)})}r=an;if(c.reinitialiseOnImageLoad){var s=a.data(E,"jScrollPaneImagesToLoad")||a("img",t);var i=[];if(s.length){s.each(function(p,ao){a(this).bind("load readystatechange",function(){if(a.inArray(p,i)==-1){i.push(ao);s=a.grep(s,function(ar,aq){return ar!=ao});a.data(E,"jScrollPaneImagesToLoad",s);var ap=a.extend(c,{reinitialiseOnImageLoad:false});t.jScrollPane(ap)}}).each(function(ap,aq){if(this.complete||this.complete===undefined){this.src=this.src}})})}}var X=this.originalSidePaddingTotal;var ai=L-c.scrollbarWidth-c.scrollbarMargin-X;var U={height:"auto",width:ai+"px"};if(c.scrollbarOnLeft){U.paddingLeft=c.scrollbarMargin+c.scrollbarWidth+"px"}else{U.paddingRight=c.scrollbarMargin+"px"}t.css(U);var V=t.outerHeight();var R=an/V;if(R<0.99){var j=t.parent();j.append(a("<div></div>").addClass("jScrollCap jScrollCapTop").css({height:c.topCapHeight}),a("<div></div>").attr({className:"jScrollPaneTrack"}).css({width:c.scrollbarWidth+"px"}).append(a("<div></div>").attr({className:"jScrollPaneDrag"}).css({width:c.scrollbarWidth+"px"}).append(a("<div></div>").attr({className:"jScrollPaneDragTop"}).css({width:c.scrollbarWidth+"px"}),a("<div></div>").attr({className:"jScrollPaneDragBottom"}).css({width:c.scrollbarWidth+"px"}))),a("<div></div>").addClass("jScrollCap jScrollCapBottom").css({height:c.bottomCapHeight}));var aj=a(">.jScrollPaneTrack",j);var u=a(">.jScrollPaneTrack .jScrollPaneDrag",j);var al;var g=[];var Z;var S=function(){if(Z>4||Z%4==0){ah(ae+al*I)}Z++};if(c.enableKeyboardNavigation){j.bind("keydown.jscrollpane",function(p){switch(p.keyCode){case 38:al=-1;Z=0;S();g[g.length]=setInterval(S,100);return false;case 40:al=1;Z=0;S();g[g.length]=setInterval(S,100);return false;case 33:case 34:return false;default:}}).bind("keyup.jscrollpane",function(ao){if(ao.keyCode==38||ao.keyCode==40){for(var p=0;p<g.length;p++){clearInterval(g[p])}return false}})}if(c.showArrows){var P;var y;var o=function(p){a("html").unbind("mouseup",o);P.removeClass("jScrollActiveArrowButton");clearInterval(y)};var H=function(){a("html").bind("mouseup",o);P.addClass("jScrollActiveArrowButton");Z=0;S();y=setInterval(S,100)};j.append(a("<a></a>").attr({href:"javascript:;",className:"jScrollArrowUp",tabindex:-1}).css({width:c.scrollbarWidth+"px",top:c.topCapHeight+"px"}).html("Scroll up").bind("mousedown",function(){P=a(this);al=-1;H();this.blur();return false}).bind("click",b),a("<a></a>").attr({href:"javascript:;",className:"jScrollArrowDown",tabindex:-1}).css({width:c.scrollbarWidth+"px",bottom:c.bottomCapHeight+"px"}).html("Scroll down").bind("mousedown",function(){P=a(this);al=1;H();this.blur();return false}).bind("click",b));var v=a(">.jScrollArrowUp",j);var m=a(">.jScrollArrowDown",j)}if(c.arrowSize){r=an-c.arrowSize-c.arrowSize;ac+=c.arrowSize}else{if(v){var aa=v.height();c.arrowSize=aa;r=an-aa-m.height();ac+=aa}}r-=c.topCapHeight+c.bottomCapHeight;aj.css({height:r+"px",top:ac+"px"});var af=a(this).css({position:"absolute",overflow:"visible"});var d;var F;var I;var ae=0;var C=R*an/2;var G=function(ao,aq){var ap=aq=="X"?"Left":"Top";return ao["page"+aq]||(ao["client"+aq]+(document.documentElement["scroll"+ap]||document.body["scroll"+ap]))||0};var O=function(){return false};var ad=function(){W();d=u.offset(false);d.top-=ae;F=r-u[0].offsetHeight;I=2*c.wheelSpeed*F/V};var e=function(p){ad();C=G(p,"Y")-ae-d.top;a("html").bind("mouseup",z).bind("mousemove",Q);if(a.browser.msie){a("html").bind("dragstart",O).bind("selectstart",O)}return false};var z=function(){a("html").unbind("mouseup",z).unbind("mousemove",Q);C=R*an/2;if(a.browser.msie){a("html").unbind("dragstart",O).unbind("selectstart",O)}};var ah=function(ao){j.scrollTop(0);ao=ao<0?0:(ao>F?F:ao);ae=ao;u.css({top:ao+"px"});var ap=ao/F;t.data("jScrollPanePosition",(an-V)*-ap);af.css({top:((an-V)*ap)+"px"});t.trigger("scroll");if(c.showArrows){v[ao==0?"addClass":"removeClass"]("disabled");m[ao==F?"addClass":"removeClass"]("disabled")}};var Q=function(p){ah(G(p,"Y")-d.top-C)};var Y=Math.max(Math.min(R*(an-c.arrowSize*2),c.dragMaxHeight),c.dragMinHeight);u.css({height:Y+"px"}).bind("mousedown",e);var T;var w;var l;var ab=function(){if(w>8||w%4==0){ah((ae-((ae-l)/2)))}w++};var ak=function(){clearInterval(T);a("html").unbind("mouseup",ak).unbind("mousemove",N)};var N=function(p){l=G(p,"Y")-d.top-C};var A=function(p){ad();N(p);w=0;a("html").bind("mouseup",ak).bind("mousemove",N);T=setInterval(ab,100);ab();return false};aj.bind("mousedown",A);j.bind("mousewheel",function(ao,aq){aq=aq||(ao.wheelDelta?ao.wheelDelta/120:(ao.detail)?-ao.detail/3:0);ad();W();var ap=ae;ah(ae-aq*I);var p=ap!=ae;return !p});var f;var D;function J(){var p=(f-ae)/c.animateStep;if(p>1||p<-1){ah(ae+p)}else{ah(f);W()}}var W=function(){if(D){clearInterval(D);delete f}};var ag=function(aq,p){if(typeof aq=="string"){$e=a(aq,t);if(!$e.length){return}aq=$e.offset().top-t.offset().top}W();var ap=V-an;aq=aq>ap?ap:aq;t.data("jScrollPaneMaxScroll",ap);var ao=aq/ap*F;if(p||!c.animateTo){ah(ao)}else{j.scrollTop(0);f=ao;D=setInterval(J,c.animateInterval)}};t[0].scrollTo=ag;t[0].scrollBy=function(ao){var p=-parseInt(af.css("top"))||0;ag(p+ao)};ad();ag(-am,true);a("*",this).bind("focus",function(ar){var aq=a(this);var au=0;while(aq[0]!=t[0]){au+=aq.position().top;aq=aq.offsetParent()}var p=-parseInt(af.css("top"))||0;var at=p+an;var ap=au>p&&au<at;if(!ap){var ao=au-c.scrollbarMargin;if(au>p){ao+=a(this).height()+15+c.scrollbarMargin-an}ag(ao)}});if(location.hash&&location.hash.length>1){setTimeout(function(){ag(location.hash)},a.browser.safari?100:0)}a(document).bind("click",function(ao){$target=a(ao.target);if($target.is("a")){var p=$target.attr("href");if(p&&p.substr(0,1)=="#"&&p.length>1){setTimeout(function(){ag(p,!c.animateToInternalLinks)},a.browser.safari?100:0)}}});function B(p){a(document).bind("mousemove.jScrollPaneDragging",x);a(document).bind("mouseup.jScrollPaneDragging",n)}var M;var h;function K(){direction=M<0?-1:1;t[0].scrollBy(M/2)}function k(){if(h){clearInterval(h);h=undefined}}function x(ap){var aq=t.parent().offset().top;var p=aq+an;var ao=G(ap,"Y");M=ao<aq?ao-aq:(ao>p?ao-p:0);if(M==0){k()}else{if(!h){h=setInterval(K,100)}}}function n(p){a(document).unbind("mousemove.jScrollPaneDragging").unbind("mouseup.jScrollPaneDragging");k()}j.bind("mousedown.jScrollPane",B);a.jScrollPane.active.push(t[0])}else{t.css({height:an+"px",width:L-this.originalSidePaddingTotal+"px",padding:this.originalPadding});t[0].scrollTo=t[0].scrollBy=function(){};t.parent().unbind("mousewheel").unbind("mousedown.jScrollPane").unbind("keydown.jscrollpane").unbind("keyup.jscrollpane")}})};a.fn.jScrollPaneRemove=function(){a(this).each(function(){$this=a(this);var b=$this.parent();if(b.is(".jScrollPaneContainer")){$this.css({top:"",height:"",width:"",padding:"",overflow:"",position:""});$this.attr("style",$this.data("originalStyleTag"));b.after($this).remove()}})};a.fn.jScrollPane.defaults={scrollbarWidth:10,scrollbarMargin:5,wheelSpeed:18,showArrows:false,arrowSize:0,animateTo:false,dragMinHeight:1,dragMaxHeight:99999,animateInterval:100,animateStep:3,maintainPosition:true,scrollbarOnLeft:false,reinitialiseOnImageLoad:false,tabIndex:0,enableKeyboardNavigation:true,animateToInternalLinks:false,topCapHeight:0,bottomCapHeight:0};a(window).bind("unload",function(){var c=a.jScrollPane.active;for(var b=0;b<c.length;b++){c[b].scrollTo=c[b].scrollBy=null}})})(jQuery);
/* jquery mousewheel Copyright (c) 2006 Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net) */
(function(a){a.event.special.mousewheel={setup:function(){var b=a.event.special.mousewheel.handler;if(a.browser.mozilla){a(this).bind("mousemove.mousewheel",function(c){a.data(this,"mwcursorposdata",{pageX:c.pageX,pageY:c.pageY,clientX:c.clientX,clientY:c.clientY})})}if(this.addEventListener){this.addEventListener((a.browser.mozilla?"DOMMouseScroll":"mousewheel"),b,false)}else{this.onmousewheel=b}},teardown:function(){var b=a.event.special.mousewheel.handler;a(this).unbind("mousemove.mousewheel");if(this.removeEventListener){this.removeEventListener((a.browser.mozilla?"DOMMouseScroll":"mousewheel"),b,false)}else{this.onmousewheel=function(){}}a.removeData(this,"mwcursorposdata")},handler:function(d){var b=Array.prototype.slice.call(arguments,1);d=a.event.fix(d||window.event);a.extend(d,a.data(this,"mwcursorposdata")||{});var e=0,c=true;if(d.wheelDelta){e=d.wheelDelta/120}if(d.detail){e=-d.detail/3}d.data=d.data||{};d.type="mousewheel";b.unshift(e);b.unshift(d);return a.event.handle.apply(this,b)}};a.fn.extend({mousewheel:function(b){return b?this.bind("mousewheel",b):this.trigger("mousewheel")},unmousewheel:function(b){return this.unbind("mousewheel",b)}})})(jQuery);


//Copyright 2009 FriendFeed
// chat.js
$(document).ready(function() {
    $("#messageform").live("submit", function() {
        newMessage($(this));
        return false;
    });
    $("#messageform").live("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });
    $("#message").select();
    updater.poll();
    scrollPane();
});

var $inbox = $('#tweet-container');

function scrollPane() {
    $inbox.jScrollPane({scrollbarWidth: 10});
    $inbox[0].scrollTo($inbox.data('jScrollPaneMaxScroll'));
}

function newMessage(form) {
    var message = form.formToDict();
    var disabled = form.find("input[type=submit]");
    disabled.disable();
    $.postJSON("/talk/new/" + window.BPC, message, function(response) {
        updater.showMessage(response);
        if (message.id) {
            form.parent().remove();
        } else {
            form.find("input[type=text]").val("").select();
            disabled.enable();
        }
    });
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = $.cookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "json", type: "POST",
        success: function(response) {
    if (callback) callback(response);
    }, error: function(response) {
    	console.log("ERROR:", response)
    }});
};


var _t =
"<div class='tweet' id='m${id}'>" +
"<div class='avatar'><img src='/static/uploads/avatars/avatar2.png' /></div>" +
"<div class='user'><a target='_blank' href='/profile/${from}'>${from}</a></div>" + 
"<div class='time'><span class='datetime' title='${date}'>${date}</span></div>" +
"<div class='txt'>${body}</div>" + 
"</div>";
        
var updater = {
    errorSleepTime: 2000,
    cursor: null,
    template: $.template(_t),
    
    poll: function() {
        var args = {"_xsrf": $.cookie("_xsrf")};
        if (updater.cursor) args.cursor = updater.cursor;
        $.ajax({
        	url: "/talk/updates/" + window.BPC, 
        	type: "POST",
        	dataType: "json",
            data: args, 
            success: updater.onSuccess,
            error: updater.onError
        });
    },

    onSuccess: function(response) {
        try {
            updater.newMessages(response);
        } catch (e) {
            updater.onError();
            return;
        }
        updater.errorSleepTime = 1000;
        window.setTimeout(updater.poll, 0);
    },

    onError: function(response) {
        updater.errorSleepTime *= 2;
        console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
        window.setTimeout(updater.poll, updater.errorSleepTime);
    },

    newMessages: function(response) {
        if (!response.messages) {
        	console.log("no update");
        	return;
        }
        updater.cursor = response.cursor;
        var messages = response.messages;
        updater.cursor = parseInt(messages[messages.length - 1].id);
        console.log(messages.length, "new messages, cursor:", updater.cursor);
        for (var i = 0; i < messages.length; i++) {
            updater.showMessage(messages[i]);
        }
    },

    showMessage: function(message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        var node = $(message.html);
        d = new Date(message['ts']);
        message['date'] = R.formatTimeDelta(R.parseISO8601(message['date']));
        $inbox.append(updater.template, message);
        $inbox.data('jScrollPaneMaxScroll', $inbox.data('jScrollPaneMaxScroll') + node.height())
        scrollPane();
        $inbox.slideDown();
    }
};