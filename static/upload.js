// put this here to avoid being parsed by tornado.template
var h = "<div class='thumb tt' title='Click to insert ${title}'>" +
			"<a href='#' onclick=\"insert_to_rte(${no})\">" +
			"<img src='${src}' />" +
			"<span>${no}</span></a>" +
		"</div>";
var attachmentTemplate = $.template(h);
$.fn.attachments.defaults.template = attachmentTemplate;
$_attachments = $(':input[name=attachments]');
$_attachments.attachments();
