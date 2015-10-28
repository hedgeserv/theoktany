class User(object):
    """Represents an OKTA user

    :param first_name: the user's first name
    :type first_name: str
    :param last_name: the user's last name
    :type last_name: str
    :param email: the user's email address
    :type email: str
    :param login: the user's login (username). Defaults to email.
    :type login: str
    :param phone_number: the user's phone number
    :type phone_number: str
    :param id: the user's OKTA id
    :type id: str
    """

    def __init__(self, first_name, last_name, email, login=None, phone_number=None, id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.login = login or self.email
        self.phone_number = phone_number
