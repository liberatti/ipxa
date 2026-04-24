local _M = {}

function _M.parse_countries(str)
    local t = {}
    if not str then return t end

    for code in string.gmatch(str, "([^,]+)") do
        code = string.upper((code:gsub("%s+", "")))
        t[code] = true
    end

    return t
end

function _M.get_header(headers, name)
    if not headers then return nil end
    return headers[string.lower(name)]
end

function _M.get_client_ip(r)
    return r.useragent_ip
end

function _M.respond(r, code, msg, headers)
    if headers then
        for k, v in pairs(headers) do
            r.headers_out[k] = tostring(v)
        end
    end
    r.status = code
    r.content_type = "application/json"
    return code
end

return _M