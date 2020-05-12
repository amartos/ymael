import platform
import keyring
from keyring.backends import SecretService,Windows

import logging
logger = logging.getLogger(__name__)


class Secrets:

    def __init__(self, domain):
        system = platform.system()
        if system == "Windows":
            keyring.set_keyring(Windows.WinVaultKeyring())
        elif system == "Linux":
            keyring.set_keyring(SecretService.Keyring())

        self._domain = domain
        self._login = keyring.get_password("Ymael", self._domain)
        self._password = None
        if self._login:
            self._password = keyring.get_password("Ymael", self._login)

    def get_secrets(self):
        return (self._login, self._password)

    def set_secrets(self, secrets): # (login, password)
        self._login, self._password = secrets
        keyring.set_password('Ymael', self._domain, self._login)
        keyring.set_password('Ymael', self._login, self._password)
