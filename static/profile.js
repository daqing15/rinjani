$('.account .rm').live('click', function() {
    $parent = $(this).parents('.account')
    if ($parent.find('input[type=hidden]').val() != "0") {
        if (!confirm("Are you sure?")) {
            return false;
        }
    }
    $parent.remove();
    if ($('.account').length < 1) { $('.account-header').hide(); }
});

$account = $('.accountsrc').clone(true).removeClass('accountsrc').addClass('account');

$('.cp').click(function() {
    $new_account = $account.clone(true);
    $new_account.find(':input').each(function() {
        $i = $(this)
        if ($i.attr('name') != undefined) {
            idx = $i.attr('name') + ($('.account').length + 1);
            $i.attr('name', idx);
        }
    })
    $('.accounts').append($new_account.show());
    if ($('.account').length > 0) { $('.account-header').show(); }
    return false;
});