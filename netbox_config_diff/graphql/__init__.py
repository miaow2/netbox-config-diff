from netbox.settings import VERSION

if VERSION.startswith("3."):
    from .old.schema import schema  # noqa
else:
    from .new.schema import schema  # noqa
