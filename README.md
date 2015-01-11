# LittleServerExecuter
LSE is the simplest python app that help instantly run systemd services (apache, mysql, postgresql, nginx + php-fpm)

To start working throug the LSE, you need to set up the settings.json file.

It might look like this:
{
	"app": {
		"pidfile": "/tmp/pndcc.pid",
		"rootapp": "pkexec",
		"systemcontrol": "systemctl"
	},
	"services": {
		"nginx": {
			"1": {
				"name": "nginx",
				"pid": "/run/nginx.pid"
			},
			"2": {
				"name": "php-fpm",
				"pid": "/opt/pndcc/pids/php-fpm.pid"
			}
		},
		"httpd": {
			"1": {
				"name": "httpd",
				"pid": "/run/httpd/httpd.pid"
			}
		},
		"postgres": {
			"1": {
				"name": "postgresql",
				"pid": "/opt/pndcc/pids/postgres.pid"
			}
		},
		"mysqld": {
			"1": {
				"name": "mysqld",
				"pid": "/run/mysqld/mysqld.pid"
			}
		}
	}
}

If you wanna start working immediatelly just fix the "pid" lines to the correct locations of services pid files.
And maybe even little bit fix the "name" lines of the correct names of your services.

!!! This is the simples implementation. In a future application become more simple and useful.
