function handle(r)
    local status = tonumber(r.subprocess_env["REDIRECT_STATUS"]) or r.status
    r:err("ipxa [debug]: handle_error called for status " .. tostring(status))
    local message = "An unexpected error occurred"
    
    local errors = {
        [400] = "Bad Request",
        [401] = "Unauthorized",
        [403] = "Forbidden",
        [404] = "Not Found",
        [405] = "Method Not Allowed",
        [500] = "Internal Server Error",
        [502] = "Bad Gateway",
        [503] = "Service Unavailable",
        [504] = "Gateway Timeout"
    }

    if errors[status] then
        message = errors[status]
    end

    local request_id = r.subprocess_env["UNIQUE_ID"] or "unavailable"
    
    r.err_headers_out["X-Request-Id"] = request_id
    r.err_headers_out["Content-Type"] = "application/json"
    r.err_headers_out["Server"] = ""
    r.content_type = "application/json"
    
    -- Force status 200 to bypass Apache's internal error templates
    r.status = 200

    local json = string.format('{"status": %d, "error": "%s", "message": "%s", "request_id": "%s"}', status, message, message, request_id)
    r:puts(json)
    return apache2.DONE
end
