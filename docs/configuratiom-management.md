# Usage

With plugin you can push rendered configuration from NetBox to devices.

Supported platforms:

* `arista_eos`
* `cisco_iosxe`
* `cisco_iosxr`
* `cisco_nxos`
* `juniper_junos`

Plugin using [scrapli-cfg](https://github.com/scrapli/scrapli_cfg) for this feature.

## Substitutes

If you render not full configuration, it is acceptable to pull missing config sections from the actual configuration to render full configuration.

!!! note
    If you render full configuration in NetBox, you can proceed to `Configuration Request` part

To do that you should create substitute.

Substitutes is a "tag" that needs to be replaced with output from the real device, and a regex pattern that "pulls" this section from the actual device itself.

![Screenshot of the substitute](media/screenshots/substitute.png)

In screenshot below we add substitute for Arista PlatformSetting

* **Name** is a "tag", you should put this as jinja2 variable in your config template in NetBox
* **Regexp** is a regex, that "pulls" what matched from device and replace `Name` jinja2 variable in config template

In example substitute `ethernet_interfaces` section will be replaced with whatever the provided pattern finds from the real device.

This pattern matches all ethernet interfaces on a Arista device.

To correctly render substitute in config template you have two options:

```
{{ "{{ ethernet_interfaces }}" }}
```

or

```
{% raw %}{{ ethernet_interfaces }}{% endraw %}
```

Config template will look like:

![Screenshot of the config template with substitute](media/screenshots/config-temp-substitute.png)

And rendered config template with substitute

![Screenshot of the rendered template with substitute](media/screenshots/render-temp-substitute.png)

## Configuration Request

Now you let's create `Configuration Request` with devices you want to configure.

!!! warning
    For request only accepts devices with `Active` status and assigned Platform, Primary IP, Config Template and PlatformSetting

Find `Configuration Requests` in navbar.

Now collect diffs for devices pressing `Collecting diffs` button.

![Screenshot of the Collecting diffs button](media/screenshots/cr-collecting-diff-button.png)

On tab `Diffs` you can review diffs for devices.

![Screenshot of the Diffs tab](media/screenshots/cr-diffs-tab.png)

To continue approve request by pressing `Approve` button.

![Screenshot of the Approve button](media/screenshots/cr-approve-button.png)

Also you can cancel approve after that.

![Screenshot of the Unapprove button](media/screenshots/cr-unapprove-button.png)

After approval you can see by whom configuration request is approved.

![Screenshot of the Approved request](media/screenshots/cr-approved.png)

At this moment you can schedule job that will push rendered configuration to devices in configuration request by pressing schedule button.

![Screenshot of the Schedule button](media/screenshots/cr-schedule-button.png)

After that you can see by whom configuration request is scheduled and time.

![Screenshot of the Scheduled request](media/screenshots/cr-scheduled.png)

Also you can cancel scheduled job by pressing `Unschedule` button.

![Screenshot of the Unschedule button](media/screenshots/cr-unschedule-button.png)

!!! warning
    Approve and Schedule buttons is accessable only to user with `netbox_config_diff.approve_configurationrequest`
    permission

!!! warning
    If you unapprove scheduled configuration request, scheduled job will be canceled

After scheduled job is completed you can job logs on configuration request page.

![Screenshot of the Unschedule button](media/screenshots/cr-job-log.png)

!!! note
    Completed configuration requests can't be edited.

## Rollback

If an error occurs while executing a job that pushes configurations to devices then all configured devices will be rollbacked to the previous version of the configuration.
