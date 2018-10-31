"""
Fence's login endpoints must redirect only to valid URLs:

    - the same application (``BASE_URL``)
    - registered in the configuration
    - registered for an OAuth client
"""


def test_valid_redirect(client, oauth_client):
    """
    Check that a valid redirect is allowed. Here we use the URL from the test OAuth
    client.
    """
    response = client.get("/login/google?redirect={}".format(oauth_client.url))
    assert response.status_code == 302


def test_invalid_redirect_fails(client):
    """
    Check that giving a bogus redirect to the login endpoint returns an error.
    """
    response = client.get("/login/google?redirect=https://evil-site.net")
    assert response.status_code == 400
