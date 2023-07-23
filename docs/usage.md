
# Usage

Under `Plugins` navbar menu you can find plugin

![Screenshot of navbar](media/screenshots/navbar.png)

Add PlatformSetting objects for your platforms in NetBox.

Define:

- **Driver** for Scrapli, you can find all drivers in [Scrapli](https://github.com/carlmontanari/scrapli) and [Scrapli community](https://github.com/scrapli/scrapli_community) documentation.
- **Command** to collect configuration
- Optional regex patterns to exclude from actual config, specify each pattern on a new line

With regexps you can exclude big parts of the configuration and compare tiny configuration pieces (only ntp configuration).

You can test regexp on the site https://regex101.com/.

![Screenshot of PlatformSetting](media/screenshots/platformsetting.png)

Plugin adds a custom script `ConfigDiffScript` that runs all logic about diff calculations and connections to devices.
You can find scripts list in navbar `Customization -> Scripts`.

![Screenshot of the scripts list](media/screenshots/script-list.png)

In the script, you can define a site, on which devices run compliance, or devices.
 If you define both fields, script will run only on devices from `Devices` field

> **Warning**
>
> Script runs only on devices with status `Active`, assigned Primary IP, Platform and PlatformSetting

If you have configs in NetBox DataSource, you can define it, the script instead of connecting to devices will find configs in DataSource by device's names.

> **Warning**
>
> Be sure that DataSource is synced and has the latest data

> **Note**
>
> Only synced DataSources are acceptable

![Screenshot of the script](media/screenshots/script.png)

After script is done you can find results in `Config Compliances` menu. Each device has its own result.

![Screenshot of the compliance list](media/screenshots/compliance-list.png)

Also result is storing rendered and actual configurations from devices.

Compliance finished with error

![Screenshot of the compliance error](media/screenshots/compliance-error.png)

Render diff between configurations

![Screenshot of diff](media/screenshots/compliance-diff.png)

No diff

![Screenshot of the compliance ok](media/screenshots/compliance-ok.png)