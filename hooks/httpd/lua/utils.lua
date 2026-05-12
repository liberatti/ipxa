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
    local request_id = r.subprocess_env["UNIQUE_ID"] or "unavailable"
    r.err_headers_out["X-Request-Id"] = request_id
    r.err_headers_out["Server"] = ""

    if headers then
        for k, v in pairs(headers) do
            r.err_headers_out[k] = tostring(v)
        end
    end

    r.status = code
    r.content_type = "application/json"
    
    local message = msg or "Access Denied"
    r:err(string.format("[%s] %s", request_id, message))
    
    local json = string.format('{"status": %d, "error": "Forbidden", "message": "%s", "request_id": "%s"}', code, message, request_id)
    
    r:puts(json)
    return apache2.DONE
end

return _M