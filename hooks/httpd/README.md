# Apache2 lua test

## Install packages

```bash
yum install -y epel-release
yum install -y httpd mod_lua lua-socket
```

## Configuration

Create folders and copy files:

```bash
mkdir -p /etc/httpd/lua
cp samples/httpd/lua/*.lua /etc/httpd/lua/
```

Config file `/etc/httpd/lua/config.lua`:

```lua
local config = {
    API = "http://[IP_ADDRESS]",
    BLOCKED_COUNTRIES = "CN,RU,KP"
}
return config
```

Run test:

```bash
cd /etc/httpd/lua
lua test.lua
```

Output:

```text
[LOG]	IPXA GEO BLOCK: 14.152.94.1 country=CN
RESULT:	403
```

## Apache config

Edit `/etc/httpd/conf/httpd.conf` and add:

```apacheconf
<VirtualHost *:80>
    ServerName exemplo.com
    DocumentRoot /var/www/html
    LuaHookAccessChecker /etc/httpd/lua/ipxa.lua ip_info_check
</VirtualHost>
```

```bash
# Run Apache
systemctl enable --now httpd
```
