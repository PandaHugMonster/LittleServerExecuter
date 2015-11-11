# LittleServerExecuter
LSE is the simplest python app that helps instantly run systemd services
(like apache, mysql, postgresql, nginx, php-fpm and etc.)

#### Big changes

##### Version 0.4.2 (current)
 * Changed UI
 * Added elements for future Apache configs updating functions
 * Added elements for future functions to update config of the application
 * Fixed bug #1
 * Prepared migrating to a new standards

##### Version 0.4.1 (previous)
 * Disabled button when not authorized to do actions.
 * Documented some lines.
 * Every Service in the config file will appear as the button in the app
 * Changed UI (Used HeaderBars)
 * Fixed some Labels
 * Updated functions
 * Added ability to start/stop all services by 1 click


#### Notes

1. To have ability to switchon or switchoff you need to run application
as root
2. Little Server Executer is going to be the part
of a new system called Panda's Control Centre

#### Known bugs

#### Settings Example
```json
{
	"app": {
		"pidfile": "/tmp/pndcc.pid"
	},
	"services": {
		"httpd.service": "Apache server",
		"postgresql.service": "Postgres server",
		"mysqld.service": "MySQL server"
	}
}
````
