local _M = {}

function _M.new(maxsize, ttl)
    local self = {}

    local cache = {}
    local order = {}
    local CACHE_TTL = ttl or 30
    local MAX_SIZE = maxsize or 1000

    local function now()
        return os.time()
    end

    local function remove_lru()
        local oldest_key = table.remove(order, 1)
        if oldest_key then
            cache[oldest_key] = nil
        end
    end

    local function touch(key)
        for i, k in ipairs(order) do
            if k == key then
                table.remove(order, i)
                break
            end
        end
        table.insert(order, key)
    end

    function self.get(key)
        local entry = cache[key]
        if not entry then return nil end

        if now() - entry.timestamp > CACHE_TTL then
            cache[key] = nil
            return nil
        end

        touch(key)
        return entry.data
    end

    function self.set(key, data)
        if not cache[key] and #order >= MAX_SIZE then
            remove_lru()
        end

        cache[key] = {
            data = data,
            timestamp = now()
        }

        touch(key)
    end

    function self.size()
        return #order
    end

    return self
end

return _M