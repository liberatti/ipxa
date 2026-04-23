local http = require "socket.http"
local ltn12 = require "ltn12"

local function parse_countries(str)
    local t = {}
    if not str then return t end

    for code in string.gmatch(str, "([^,]+)") do
        code = string.upper(string.gsub(code, "%s+", ""))
        t[code] = true
    end

    return t
end

local function get_header(headers, name)
    if not headers then return nil end
    name = string.lower(name)

    for k, v in pairs(headers) do
        if string.lower(k) == name then
            return v
        end
    end
    return nil
end

function ip_info_check(r)
    local ip = r.useragent_ip

    local api_base = r.subprocess_env["IPXA_API"]
    local blocked_env = r.subprocess_env["IPXA_BLOCKED_COUNTRIES"]

    local blocked_countries = parse_countries(blocked_env)

    local url = api_base .. "/api/ip/info/" .. ip
    local response_body = {}

    local res, code, headers = http.request{
        url = url,
        method = "GET",
        sink = ltn12.sink.table(response_body)
    }

    if code ~= 200 then
        return apache2.DECLINED
    end
    local ignore = get_header(headers, "X-Ignore")

    if ignore and ignore == "true" then
        return apache2.DECLINED
    end

    local country_code = get_header(headers, "X-Country-Code")

    if not country_code then
        local body = table.concat(response_body)
        country_code = string.match(body, '"country_code"%s*:%s*"([A-Z]+)"')
    end

    if country_code then
        country_code = string.upper(country_code)
    end

    if country_code and blocked_countries[country_code] then
        r:err("IPXA GEO BLOCK: " .. ip .. " country=" .. country_code)
        return 403
    end

    local risk_score = tonumber(get_header(headers, "X-Risk-Score") or -1) or -1

    if risk_score == -1 then
        local body = table.concat(response_body)
        local score = string.match(body, '"risk_score"%s*:%s*(%d+)')
        if score then
            risk_score = tonumber(score)
        end
    end

    if risk_score > 0 then
        r:err("IPXA BLOCK: " .. ip .. " risk=" .. risk_score)
        return 403
    end

    return apache2.DECLINED
end