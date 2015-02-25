# LittleServerExecuter
LSE is the simplest python app that help instantly run systemd services (apache, mysql, postgresql, nginx, php-fpm)

== Big changes ==

[version 0.4.0]
 * Removed unneeded functions.
 * Documented some lines.
 * Replaced pyinotify implementation with DBus + Systemd (URAH!!!)
 * Fixed some methods
 * Works well as the simplest solution
 
To have ability to switchon or switchoff you need to runn application
as root (or you have to have permissions to use systemd as a regular user)

== Some Little Info ==

Little Server Executer is going to be the part 
of a new system called Panda's Control Centre
