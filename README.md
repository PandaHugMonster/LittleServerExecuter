# LittleServerExecuter
LSE is the simplest python app that helps instantly run systemd services
(like apache, mysql, postgresql, nginx, php-fpm and etc.)
! You can configure which services you need to control with the settings.json

![alt tag](https://github.com/PandaHugMonster/LittleServerExecuter/blob/develop/picture_preview_v0.4.4.png)

#### Big changes

##### Version 0.4.4 (current)
 * Added spinners for longtime-startup-services (Glassfish for example)
 * Added service glassfish to list of services
 * Rewritten authorization model (Now no need to be root for running script to manage services, PolKit used to authorize)
 * Minimal optimization of the code
 * Fixed multiple execution of the systemd action
 * Removed warning: "Gtk-WARNING **: Overriding tab label for notebook"
 * Added PHP modules and php.ini observers

##### Version 0.4.3 (previous)
 * List of apache's modules
 * View of Apache httpd.conf config
 * View of Mysql my.cnf config
 * Updated some code
 * Updated some UI elements


#### Notes

1. Little Server Executer is going to be the part
of a new system called Panda's Control Centre
2. This project does not contain the best style of development-code - this is related
to the really important moment: This project is my GTK+Python3 experiment, so later
code will be in a better shape. Arguing about that my absolutely unlogical code -
will be deleted - because I'm well informed about this problem, and it exists only
because of experimenting, and doesn't reflect my tallents. Thank you for your understanding

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
