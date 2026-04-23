# Apache2 lua test

## EL7x

Install packages:

```bash
yum install lua-socket
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

## EL8x

```bash
yum install luasocket
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
