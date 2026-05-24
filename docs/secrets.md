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

Script will find secrets with these roles and use them as credentials in this order:

1. Device secrets
2. Device role secrets (if [enabled](https://github.com/Onemind-Services-LLC/netbox-secrets/blob/master/docs/installation.md#apps))
3. Platform secrets (if enabled)

The first non-empty value found for each credential is used.

You can change the precedence order via plugin configuration `SECRETS_PRECEDENCE`. It accepts a list of attribute names that will be resolved against the `Device` object. Use the special name `device` to refer to the device itself. Invalid names are ignored. Default value:

```python
PLUGINS_CONFIG = {
    "netbox_config_diff": {
        "SECRETS_PRECEDENCE": ["device", "role", "platform"],
    }
}
```

Also you can define secret role for desired privilege level in plugins variable `DEFAULT_DESIRED_PRIVILEGE_LEVEL_ROLE`
 or can specify the desired privilege level itself in variable `DEFAULT_DESIRED_PRIVILEGE_LEVEL`.

If no matching secret is found (or a secret cannot be decrypted), credentials from `PLUGINS_CONFIG` are used.
