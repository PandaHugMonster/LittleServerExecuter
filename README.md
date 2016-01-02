# LittleServerExecuter (branch "develop")
LSE is the simplest python app that helps instantly run systemd services
(like apache, mysql, postgresql, nginx, php-fpm and etc.)
! You can configure which services you need to control with the settings.json

![alt tag](https://github.com/PandaHugMonster/LittleServerExecuter/blob/develop/picture_preview_v0.4.4.png)

#### Big changes

##### Version 0.4.4 (in progress)
 * Added spinners for longtime-startup-services (Glassfish for example)
 * Added service glassfish to list of services
 * Rewritten authorization model (Now no need to be root for running script to manage services, PolKit used to authorize)
 * Minimal optimization of the code
 * Fixed multiple execution of the systemd action
 * Removed warning: "Gtk-WARNING **: Overriding tab label for notebook"
 * Added PHP modules and php.ini observers

#### Settings Example
```json
{
	"app": {
		"pidfile": "/tmp/pndcc.pid"
	},
	"services": {
		"Devices": {
			"bluetooth.service": "Bluetooth service",
			"colord.service": "Manage, Install and Generate Color Profiles",
			"udisks2.service": "Disk Manager"
		},
		"Web Group": {
			"httpd.service": "Apache server"
		},
		"Other": {
			"upower.service": "Daemon for power management",
			"geoclue.service": "Location Lookup Service"
		}
	}
}
````
