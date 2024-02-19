import ipaddress

# Cache dictionary to store results of IP checks
_ip_cache = {}


def is_private_ip(ip):
    def is_private_ip_store():
        result = ipaddress.ip_address(ip).is_private
        _ip_cache[ip] = result
        return result
    """Check if the given IP address is private, with caching."""
    # Use the get method to retrieve the result from the cache, if available
    # result = _ip_cache.get(ip)
    #
    # if result is not None:
    #     return result

    return is_private_ip_store() if None else _ip_cache.get(ip)

    # # Check if the IP is private and store the result in the cache
    # result = ipaddress.ip_address(ip).is_private
    # _ip_cache[ip] = result
    # return result


def is_private_ip_0(ip):
    """Check if the given IP address is private."""
    return ipaddress.ip_address(ip).is_private

