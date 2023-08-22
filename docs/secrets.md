# Integration with NetBox secrets plugin

You can store credentials for devices authentification in NetBox secrets [plugin](https://github.com/Onemind-Services-LLC/netbox-secrets).

Read NetBox secrets docs for more info.

In plugin variables define secrets roles for username (`USER_SECRET_ROLE`) and password (`PASSWORD_SECRET_ROLE`).

Default values for this variables are:

```python
PLUGINS_CONFIG = {
    "netbox_config_diff": {
        "USER_SECRET_ROLE": "Username",
        "PASSWORD_SECRET_ROLE": "Password",
    },
}
```

Script will find secrets with these roles attached to the device and use them as credentials.

If something goes wrong, then credentials from `PLUGINS_CONFIG` will be used.
