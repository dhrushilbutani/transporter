from odoo.addons.web.controllers.home import Home as WebHome
from odoo.addons.web.controllers.utils import is_user_internal


class Home(WebHome):
    def _login_redirect(self, uid, redirect=None):
        if not redirect and not is_user_internal(uid):
            redirect = '/'
        return super()._login_redirect(uid, redirect=redirect)