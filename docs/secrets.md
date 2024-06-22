# Integration with NetBox secrets plugin

You can store credentials for devices authentification in NetBox secrets [plugin](https://github.com/Onemind-Services-LLC/netbox-secrets).
 Read NetBox secrets docs for more info.

In plugin variables define secrets roles for username (`USER_SECRET_ROLE`), password (`PASSWORD_SECRET_ROLE`) and
 password (`SECOND_AUTH_SECRET_ROLE`) for Privileged EXEC mode.

Default values for this variables are:

```python
PLUGINS_CONFIG = {
    "netbox_config_diff": {
        "USER_SECRET_ROLE": "Username",
        "PASSWORD_SECRET_ROLE": "Password",
        "SECOND_AUTH_SECRET_ROLE": "Second Auth",
    },
}
```

Script will find secrets with these roles attached to the device and use them as credentials.

Also you can define secret role for desired privilege level in plugins variable `DEFAULT_DESIRED_PRIVILEGE_LEVEL_ROLE`
 or can specify the desired privilege level itself in variable `DEFAULT_DESIRED_PRIVILEGE_LEVEL`.

If something goes wrong, then credentials from `PLUGINS_CONFIG` will be used.
