# LittleServerExecuter
LSE is the simplest python app that helps instantly run systemd services
(like apache, mysql, postgresql, nginx, php-fpm and etc.)
! You can configure which services you need to control with the settings.json

#### Huge Code Changes

##### Version 0.5.0 (current)
 * **Fully refactored structure of the code**
 * Partly optimized
 * Prepared for future connections to remote servers (Multiple servers control as local, as remote)
 * LSB package (/etc/lsb-release file actually) is recommended for some basic system data identifying
 * ** IMPORTANT: ** Right now only Local Machines (local-connections) are supported, so no remote control in that version.
 * ** IMPORTANT: ** Distibutives Logo right now are not fully adjusted, so logo can be missed without LSB and so on

##### Version 0.4.4 (previous)
 * Added spinners for longtime-startup-services (Glassfish for example)
 * Added service glassfish to list of services
 * Rewritten authorization model (Now no need to be root for running script to manage services, PolKit used to authorize)
 * Minimal optimization of the code
 * Fixed multiple execution of the systemd action
 * Removed warning: "Gtk-WARNING **: Overriding tab label for notebook"
 * Added PHP modules and php.ini observers


#### Notes
Code is under heavy refactoring and restructuring. Really soon new features will come.

#### Future-Features
 * Mutiple servers (Multiple Connections)
 * Cluster-control of multiple servers
 * Server-side application (the point to connect to)
 * Basic configs parsing/applying support (Parsing such configs as Apache, php.ini or MySQL my.cnf settings)
 * Connection-based filesystem monitoring/observing
 * Connection-based Update-Manager support
 * Connection-based settings
 * Connection-based notes
 * Future distribution through: DEB, RPM, Arch Packages (maybe other systems like flatpak and so on)
 * Gnome Shell Widget

#### Deep Future-Features
 * Export/Import of configs and settings
 * Connection-based (Cluster-based) script-instructions applying
 * Connection-based user control
 * Server's user control
 * Server-Documentation feature
 * Backing-Up Infrastructure
 * Ticketing (maybe)
 * Connection-based SSH-interface (But I'm not sure yet)
 * Connection-based (Cluster-based) file sharing


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
