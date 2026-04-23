-- mock do Apache
apache2 = {
    DECLINED = 0
}

-- mock request
local r = {
    useragent_ip = "14.152.94.1",
    subprocess_env = {
        IPXA_API = "http://127.0.0.1:5002",
        IPXA_BLOCKED_COUNTRIES = "CN,RU"
    },
    err = function(self, msg)
        print("[LOG]", msg)
    end,
    header = function(self, msg)
        print("[HEADER]", msg)
    end
}

dofile("ipxa.lua")

local result = ip_info_check(r)

print("RESULT:", result)