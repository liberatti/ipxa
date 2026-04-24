local http = require "socket.http"
local ltn12 = require "ltn12"
local socket = require("socket")

local config = require("config")
local cache = require("cache").new(1000,30)
local utils = require("utils")
local BLOCKED_COUNTRIES = utils.parse_countries(config.BLOCKED_COUNTRIES)

local tcp = socket.tcp()
tcp:settimeout(2)

function ip_info_check(r)
    local ip = utils.get_client_ip(r)
    local cached = cache.get(ip)

    local country_code = "--"
    local risk_score = -1

    if cached then
        country_code = cached.country_code
        risk_score = cached.risk_score
    else
        local response_body = {}
        local _, code, headers = http.request{
            url = config.API .. "/api/ip/info/" .. ip,
            method = "GET",
            sink = ltn12.sink.table(response_body),
            create = function()
                return tcp
            end 
        }

        if code ~= 200 then
            return utils.respond(r, apache2.DECLINED, "ipxa [skip/error]: " .. ip .. " code=" .. code)
        end

        if utils.get_header(headers, "x-ignore") == "true" then
            return utils.respond(r, apache2.DECLINED, "ipxa [skip/ignore]: " .. ip)
        end

        country_code = utils.get_header(headers, "x-country-code")
        risk_score = tonumber(utils.get_header(headers, "x-risk-score") or -1) or -1

        if country_code and risk_score ~= -1 then
            cache.set(ip, {country_code = country_code, risk_score = risk_score})
        end
    end

    if country_code and BLOCKED_COUNTRIES[country_code] then
        return utils.respond(r, 403, "ipxa [block/geo-ip]: " .. ip .. " country_code=" .. country_code,
            {
                ["x-country-code"] = country_code,
                ["x-risk-score"] = risk_score
            }
        )
    end

    if risk_score > 0 then
        return utils.respond(r, 403, "ipxa [block/risk-score]: " .. ip .. " risk_score=" .. risk_score,
            {
                ["x-country-code"] = country_code,
                ["x-risk-score"] = risk_score
            }
        )
    end

    return apache2.DECLINED
end