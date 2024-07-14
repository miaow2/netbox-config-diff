# Changelog


## 2.6.0 (2024-07-14)

* [#62](https://github.com/miaow2/netbox-config-diff/issues/62) Add support for NetBox 4.0

This release drops support for NetBox 3.5.

## 2.5.0 (2024-06-30)

* [#67](https://github.com/miaow2/netbox-config-diff/issues/67) Add option `default_desired_privilege_level` to plugins variables (thanks to [@cknost](https://github.com/cknost))
* [#69](https://github.com/miaow2/netbox-config-diff/issues/69) Fix logger in SecretsMixin
* [#70](https://github.com/miaow2/netbox-config-diff/issues/80) Add `escapejs` filter to diff templates

## 2.4.0 (2024-05-12)

* [#63](https://github.com/miaow2/netbox-config-diff/issues/63) Generate patch commands necessary to bring a device into its intended configuration with [hier_config](https://github.com/netdevops/hier_config)

## 2.3.0 (2024-04-11)

* [#49](https://github.com/miaow2/netbox-config-diff/issues/49) Handle junipers templates with set commands
* [#56](https://github.com/miaow2/netbox-config-diff/issues/56) Add support for NetBox 3.7
* [#57](https://github.com/miaow2/netbox-config-diff/issues/57) Reverse columns in compliance diff

## 2.2.0 (2024-02-06)

* [#47](https://github.com/miaow2/netbox-config-diff/issues/47) Move plugin to separete menu item in navbar and add tab for devices with compliance result
* [#50](https://github.com/miaow2/netbox-config-diff/issues/50) Add template field for device name in DataSource to ConfigDiffScript
* [#53](https://github.com/miaow2/netbox-config-diff/issues/53) Add netbox-rq to installation process docs

## 2.1.0 (2023-10-26)

* [#35](https://github.com/miaow2/netbox-config-diff/issues/35) Add ability to define password for accessing priviliged exec mode
* [#37](https://github.com/miaow2/netbox-config-diff/issues/37) Add `DeviceRole` field to `CollectDiffScript`
* [#38](https://github.com/miaow2/netbox-config-diff/issues/38) Remove config template filter for devices filed in forms
* [#39](https://github.com/miaow2/netbox-config-diff/issues/39) Add `Status` field to `CollectDiffScript`
* [#43](https://github.com/miaow2/netbox-config-diff/issues/43) `ConfigDiffScript` does not create empty changelog entries

## 2.0.1 (2023-10-22)

* [#33](https://github.com/miaow2/netbox-config-diff/issues/33) Fix failing migrations on fresh database install

## 2.0.0 (2023-10-18)

* [#25](https://github.com/miaow2/netbox-config-diff/issues/25) Add configuration management

## 1.2.2 (2023-09-29)

* [#28](https://github.com/miaow2/netbox-config-diff/issues/28) Add legacy ssh algorithms to support old OS versions

## 1.2.1 (2023-09-07)

* [#26](https://github.com/miaow2/netbox-config-diff/issues/26) Add dark theme for diff

## 1.2.0 (2023-08-23)

* [#20](https://github.com/miaow2/netbox-config-diff/issues/20) Add integration with [netbox-secrets](https://github.com/Onemind-Services-LLC/netbox-secrets) plugin

## 1.1.1 (2023-08-13)

* [#1](https://github.com/miaow2/netbox-config-diff/issues/1) Add tests

## 1.1.0 (2023-08-01)

* [#16](https://github.com/miaow2/netbox-config-diff/issues/16) Add missing and extra config lines

## 1.0.0 (2023-07-23)

* Publish on PyPI.

## 0.1.1 (2023-07-23)

* Add DataSoures as sources for device configurations.
* Add docs.

## 0.1.0 (2023-07-09)

* First release.
