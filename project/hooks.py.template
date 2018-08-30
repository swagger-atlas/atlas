class LocustHook:
    # You need to write at least login function for this hook

    profile = None
    auth = None

    def login(self, client):
        # This is main function
        # This should at least profile profile name and auth code
        # Also, it should update all default headers which are needed with every request
        self.update_default_headers(client)
        return self.profile, self.auth

    def update_default_headers(self, client):
        client.headers.update({"Authorization": "Token {token}".format(token=self.auth)})
