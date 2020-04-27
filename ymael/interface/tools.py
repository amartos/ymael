
def set_secrets(login, password=""):
    import keyring

    if not password:
        import getpass

        password = getpass.getpass()
    keyring.set_password('Ymael', login, password)
    return password

def get_secrets(login, cmd_line=True):
    import keyring

    return keyring.get_password("Ymael", login)

def is_url_valid(url):
    import re

    # see https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not/7160778#7160778
    url_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

    return bool(re.match(url_regex, url))
