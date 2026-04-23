# Apache2 lua test

## EL7x

Install packages:

```bash
yum install lua-socket
```


## EL8x

```bash
yum install luasocket
```

## Configuration

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


```bash
cd /etc/httpd/lua
lua test.lua
```

Output:

```text
[LOG]	IPXA GEO BLOCK: 14.152.94.1 country=CN
RESULT:	403
```
