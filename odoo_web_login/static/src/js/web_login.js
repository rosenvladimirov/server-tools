odoo.define("odoo_web_login.login", function (require) {
  "use strict";
    $('.company_logo').click(function(е){
            var $form = $(e.currentTarget).parent().closest('form');
            var login = $form.find('input[name="login"]');
            if (login.hasClass('hidden') && login.hasClass('disable')){
                login.removeClass('hidden');
                login.removeClass('disable');
            } else if (!login.hasClass('hidden') && !login.hasClass('disable')) {
                login.addClass('hidden');
                login.addClass('disable');
            }
        });
});
