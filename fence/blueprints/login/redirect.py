"""
Define the ``RedirectMixin`` class for handling redirect URL validation in the
flask-restful resources (which are in this same folder).
"""

from urlparse import urlparse

from cached_property import cached_property
import flask

from fence.errors import UserError
from fence.models import Client


class RedirectMixin(object):
    """
    Mixin to handle checking valid login redirects.

    For example, links like the following should be disallowed:

        https://gen3.datacommons.io/user/login/fence?redirect=http://external-site.com
    """

    def validate_redirect(self, url):
        """
        Complain if a given URL is not on the login redirect whitelist.

        Only callable from inside flask application context.
        """
        if url.rstrip("/") not in self.allowed_login_redirects:
            flask.current_app.logger.error(
                "expected one of: {}".format(self.allowed_login_redirects)
            )
            raise UserError("invalid login redirect URL {}".format(url))

    @cached_property
    def allowed_login_redirects(self):
        """
        Determine which redirects a login redirect endpoint (``/login/google``, etc)
        should be allowed to redirect back to after login. By default this includes the
        base URL from this flask application, and also includes the redirect URLs
        registered for any OAuth clients.

        Return:
            List[str]: allowed redirect URLs
        """
        allowed = flask.current_app.config.get("LOGIN_REDIRECT_WHITELIST", [])
        allowed.append(flask.current_app.config["BASE_URL"])
        base_url = urlparse(flask.current_app.config["BASE_URL"])
        allowed.append("{}://{}".format(base_url.scheme, base_url.netloc))
        if "fence" in flask.current_app.config.get("OPENID_CONNECT", {}):
            allowed.append(
                flask.current_app.config["BASE_URL"].rstrip("/")
                + flask.url_for("login.fencelogin")
            )
        with flask.current_app.db.session as session:
            clients = session.query(Client).all()
            for client in clients:
                allowed.extend(client.redirect_uris)
        return {url.rstrip("/") for url in allowed}
