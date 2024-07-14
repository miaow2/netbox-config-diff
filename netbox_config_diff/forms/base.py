from django.forms import ModelForm
from netbox.settings import VERSION

if VERSION.startswith("3."):
    from utilities.forms.mixins import BootstrapMixin

    class CustomForm(BootstrapMixin, ModelForm):
        pass
else:

    class CustomForm(ModelForm):
        pass
