import base64
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netbox_secrets.models import Secret


class SecretsMixin:
    def get_session_key(self) -> None:
        if "netbox_secrets_sessionid" in self.request.COOKIES:
            self.session_key = base64.b64decode(self.request.COOKIES['netbox_secrets_sessionid'])
        elif "HTTP_X_SESSION_KEY" in self.request.META:
            self.session_key = base64.b64decode(self.request.META['HTTP_X_SESSION_KEY'])
        else:
            self.session_key = None

    def get_master_key(self) -> None:
        try:
            from netbox_secrets.models import SessionKey
        except ImportError:
            return

        self.master_key = None
        self.get_session_key()
        try:
            sk = SessionKey.objects.get(userkey__user=self.request.user)
            self.master_key = sk.get_master_key(self.session_key)
        except Exception as e:
            self.log_failure(f"Can't fetch master_key: {str(e)}")

    def get_secret(self, secret: "Secret") -> str | None:
        try:
            secret.decrypt(self.master_key)
        except Exception:
            return None
        return secret.plaintext
