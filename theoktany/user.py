class User(object):
    """Represents an OKTA user"""

    def __init__(self, first_name, last_name, email, login=None, phone_number=None, id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.login = login or self.email
        self.phone_number = phone_number
