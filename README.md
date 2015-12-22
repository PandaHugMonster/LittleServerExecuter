# LittleServerExecuter

!!! New versions will be: Jan 1, 2016 !!!
Sorry for a little delay

LSE is the simplest python app that helps instantly run systemd services
(like apache, mysql, postgresql, nginx, php-fpm and etc.)
! You can configure which services you need to control with the settings.json

![alt tag](https://github.com/PandaHugMonster/LittleServerExecuter/blob/master/picture_preview_v0.4.3.png)

#### Big changes

##### Version 0.4.3 (current)
 * List of apache's modules
 * View of Apache httpd.conf config
 * View of Mysql my.cnf config
 * Updated some code
 * Updated some UI elements

##### Version 0.4.2 (previous)
 * Changed UI
 * Added elements for future Apache configs updating functions
 * Added elements for future functions to update config of the application
 * Fixed bug #1
 * Added groupping
 * Added group buttons
 * Prepared migrating to a new standards


#### Notes

1. To have ability to switchon or switchoff you need to run application
as root
2. Little Server Executer is going to be the part
of a new system called Panda's Control Centre
3. This project does not contain the best style of development-code - this is related
to the really important moment: This project is my GTK+Python3 experiment, so later
code will be in a better shape. Arguing about that my absolutely unlogical code -
will be deleted - because I'm well informed about this problem, and it exists only
because of experimenting, and doesn't reflect my tallents. Thank you for your understanding

#### Known bugs

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
