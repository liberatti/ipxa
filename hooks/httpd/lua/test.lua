apache2 = {
    DECLINED = 0
}
local r = {
    useragent_ip = "14.152.94.1",
    headers_out = {},
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