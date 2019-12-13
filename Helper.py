from string import whitespace, punctuation, ascii_letters, digits
from random import randint
from http.client import HTTPSConnection as httpConn


class Genetator:

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


class Validator:

    def validate_size(self, data, recommended_size):
        """ return is the size of the data is greater than or equal to the recommended size """
        if len(data) >= recommended_size:
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
        valid_chars = {'-', '_', '.', '+'}
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

        if res.status == 200 and res.reason == "OK":
            return True
        return False

    # def is_valid_password(self, password):
    #     pass

    # def check_data(self, data):
    #     """ This will mysqli_real_escape_string, trim, striplashes and htmlspecialchars on
    #     the args given to it
    #     @param data """
    #     print(punctuation.split())
    #     # print(punctuation)
    #     # for char in punctuation:
    #     #     print(char)
    #     #     data = '_'.join(data.split(char))
    #     # return data


# # there is an inbuilt seesion already
# def check_session():

#     if (!GLOBALS['db_connection'] || !isset(_SESSION['token']))
#         return 0;

#     return 1;


# def set_session(data):
#     """ check if session isn't started and start a new session
#     else, set session with data
#     @param data """
#     session_destroy();
#     session_start();
#     _SESSION['token'] = data;

# def generate_session_token(data):
#     """ return generate a token for the session
#     @param data """
#         delimiter '____' was intensionally used
#     return sha1(data) . "____" . data;


# def get_user_email():
#     """ return the users email based on the token set.
#     explode the session token """

#     if (!isset(_SESSION['token']))
#         return 0;
#     return explode("____", _SESSION['token'])[1];

# def encode_data(data):
#     """ return an encoded string making use of htmlentities and htmlspecialchars
#     A rigorous version is check_data(data)
#     @param data """


#     return htmlentities(htmlspecialchars(mysqli_real_escape_string(db_connection, data)));


# def decode_data(data):
#     """ return a decoded string making use of htmlspecialchars and htmlentities """
#     return htmlspecialchars_decode(html_entity_decode(data));


# def has_token_expired(token_dormancy):
#     """ return a boolean comparing, if the current time stamp is gt the time given to
#     the token to expire.
#     @param `token_dormancy`: the time given to the token to expire """

#     # get the current time stamp
#     now = date('Y-m-d H:i:s', strtotime('now'));
#         and get token_dormancy, meaning, pass the token_dormancy

#     return strtotime(now) >= strtotime(token_dormancy) ? 1 : 0;

#         redirect_to token_field.php to return enter the new token as the old token
#         has expired.

# def get_dormancy_time():
#     """ returns the token_dormancy period in `Y-m-d H:i:s` format """

#     return date('Y-m-d H:i:s', strtotime('now') + (60  30));

# def get_current_time():
#     """ returns the current time stamp in 'Y-m-d H:i:s' format """

#     return date('Y-m-d H:i:s', strtotime('now'));


# def validate_password(password):
#     """ validates passwords
#     password must be at least greater than or eqaul to eight in size,
#     password must have at least an uppercase character,
#     an lowercase character,
#     a number and
#     a special character.
#     @param password
#     @return bool """

#     is_pwd_gte_8       = strlen(password) >= 8;
#     has_uppercase_char = preg_match('@[A-Z]@', password);
#     has_lowercase_char = preg_match('@[a-z]@', password);
#     has_number         = preg_match('@[0-9]@', password);
#     has_special_char   = preg_match('@[^\w]@', password);

#     if (!is_pwd_gte_8 || !has_uppercase_char || !has_lowercase_char || !has_number || !has_special_char)
#         return 0;


#     return 1;
