from datetime import datetime
from http.client import HTTPSConnection as httpConn
from random import randint
from string import (ascii_letters, ascii_lowercase, ascii_uppercase, digits,
                    punctuation, whitespace)


class Geretator:
    """ Return generated values """

    # this token is for the change of email and password
    def generate_token(self):
        """ returns a random alphanumeric characters, given the length of the data desired.
        this random token generator def is provided by Scott.
        source: https:stackoverflow.coma137335884592338 """

        TOKEN_LENGTH = 6

        token = ""

        code_alphabet = ascii_letters + digits + "_"

        max = len(code_alphabet)

        for i in range(TOKEN_LENGTH):
            token += code_alphabet[randint(0, max - 1)]

        return token

    def get_schar_count(self, data='', sack=[]):
        """ Returns the number of specific characters in data that is in sack
        By default, data is an empty string and sack is an empty list
        Both data and list, are iterables
        If neither data or sack is set, zero in returned """

        if not data or not sack:
            return 0

        counter = 0

        for char in data:
            if char in sack:
                counter += 1

        return counter

    def get_bcrypt_hashed_passwd(self, password):
        # use bcrypt to hash the password
        return password

    def get_current_date_time(self):
        # get the current date and time
        now = datetime.now()

        # format the datetime using
        # [month, day, year, hour, minute, sec]
        # [%B, %d, %Y, %H, %M, %S] : December 2, 1996 - 13:24:20
        # return now.strftime("A%, %d %B, %Y - %H:%M:%S")
        return now.strftime("%B %d, %Y - %H:%M:%S")


class Validator:

    def validate_size(self, data, recommended_size=[6, 20]):
        """ 
        Return is the size of the data is greater than or equal to the recommended size.
        By default, the recommended size is [6, 20].
        Example: Validator().validate_size(data, [6, 20]).
        Returns True if 6 <= size of data <= 20, else False.
        """
        data_size = len(data)
        if recommended_size[0] <= data_size <= recommended_size[1]:
            return True
        return False

    def is_email_valid(self, email=""):
        """ returns a bool if a an email, is a valid one with the domain as a tuple"""

        # according to the link, these emails are valid but they fail here
        # ref on
        # email: https://stackoverflow.com/questions/2049502/what-characters-are-allowed-in-an-email-address

        # emails = [
        #     '"very.unusual.@.unusual.com"@example.com',
        #     '"very.(),:;<>[]\".VERY.\"very@\ \"very\".unusual"@strange.example.com',
        #     "#!$%&'*+-/=?^_`{}|~@example.org",
        #     '"()<>[]:,;@"!#$%&\'-/=?^_`{}| ~.a"@example.org'
        # ]

        # certain punctuations aren't allowed in an email except in a quote
        # except, space -  ' ' in a quoted local, the rest are unacceptable
        # learnt that + can be used in XSS so we'd remove it
        valid_chars = {'-', '_', '.'}
        invalid_chars = set(punctuation + whitespace) - valid_chars

        # check if email is set, it is not an empty string
        if not email:
            return False

        # strip leading and ending spaces
        email = email.strip()

        at_char = "@"
        dot = "."
        hyphen = "-"
        dbl_quote = '"'

        # thus email must have @
        if at_char not in email:
            return False

        # there must one and only one @
        if email.count(at_char) > 1:
            return False

        # split the email into local and domain part
        local, domain = email.split(at_char)

        # check for invalid characters in quote
        # any other char except, _ - ., should be in double quote
        # spaces are allowed inside the local without a quote
        for char in invalid_chars:
            if char in local and (not local.startswith(dbl_quote) or not local.endswith(dbl_quote)):
                return False

        # quote string must be dot seperated or a dot shouldn't follow a dot
        if dot in local and (local[local.index(dot)] == local[local.index(dot) + 1]):
            return False

        # local.startswith('.') and local.endswith('.') == False
        if local.startswith(dot) or local.endswith(dot):
            return False

        # domain, - can't be first or last char
        if domain.startswith(hyphen) or domain.endswith(hyphen):
            return False

        # quote string must be dot seperated or a dot shouldn't follow a dot
        # in domain
        if dot in domain and (domain[domain.index(dot)] == domain[domain.index(dot) + 1]):
            return False

        # domain, . cant't be first or last char
        if domain.startswith(dot) or domain.endswith(dot):
            return False

        return True, domain

    def email_exist(self, domain):
        """ ping the domain's server to see if the domain actuall exists
        using http.client and get a responds of 200 OK """

        conn = httpConn(domain)
        conn.request("HEAD", "/")
        res = conn.getresponse()

        if res.status != 200 or res.reason != "OK":
            return False
        return True

    def is_valid_password(self, password):
        """ returns True when the password  is valid, else False.
        The password must satisfy these conditions:
        * no leading or trailing while spaces spaces - so we strip them off
        * Should be between 6 to 20 characters long
        * must exclude any of these, {*%;<>\{}[]+=?&,:'"` } and blank space
        * must have at least one number.
        * must have at least one lowercase character.
        * must have at least one upppercase character.
        * must have at least one special symbol. {!@#$^&()_.-}.
         """
        # Conditions for a valid password are:
        if not password:
            return False, f"password is empty"

        # no leading or trailing while spaces spaces
        password = password.strip()

        # *Should be between 6 to 20 characters long. there is the notion of no max limit
        # I think the size function should handle this
        MIN_PASS_SIZE = 6
        MAX_PASS_SIZE = 20

        if not Validator().validate_size(password, [MIN_PASS_SIZE, MAX_PASS_SIZE]):
            return False, f"password size should between {MIN_PASS_SIZE} and {MAX_PASS_SIZE} inclusive"

        # avoid {*%;<>\{}[]+=?&,:'"` } and blank space
        valid_chars = {'-', '_', '.', '!', '@', '#', '$', '^', '&', '(', ')'}
        invalid_chars = set(punctuation + whitespace) - valid_chars

        for char in invalid_chars:
            if char in password:
                return False, f"Password may have special character such as {valid_chars}"

        # Should have at least one number.
        if Geretator().get_schar_count(password, digits) < 1:
            return False, "Must include at least 1 digit"

        # Should have at least one uppercase and one lowercase character.
        if Geretator().get_schar_count(password, ascii_uppercase) < 1:
            return False, "Must include at least 1 uppercase character"

        if Geretator().get_schar_count(password, ascii_lowercase) < 1:
            return False, "Must include at least 1 lowercase"

        # Should have at least one special symbol. {!@#$^&()_.-}.
        if Geretator().get_schar_count(password, valid_chars) < 1:
            return False, f"Must include at least 1 special symbol such as {valid_chars}"

        return password
