from functools import wraps

import pycountry
import pycountry_convert as pc
from basic4web.controllers.base_controller import response_data

from config import cache


def cached(prefix):
    """
    Decorator that implements a simple TTL cache for functions that take an IP as their first argument.

    Args:
        prefix (str): The prefix to use for the cache key.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(ip, *args, **kwargs):
            cache_key = f"{prefix}:{ip}"
            hit = cache.get(cache_key)
            if hit:
                headers = {
                    "X-Risk-Score": hit['security']['risk_score'],
                    "X-Cache": "HIT"
                }
                return response_data(hit, headers=headers)
            result = f(ip, *args, **kwargs)
            return result

        return wrapper

    return decorator


def enrich_country(row):
    """
    Enriches a database row with country name and continent information based on its country code.

    Args:
        row (dict): The database row (dictionary) to enrich.

    Returns:
        dict: The enriched dictionary.
    """
    code = row.get("country_code")

    if not code:
        return row

    # Country
    country = pycountry.countries.get(alpha_2=code)
    if country:
        row["country_name"] = country.name

    # Continent
    try:
        continent_code = pc.country_alpha2_to_continent_code(code)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        row["continent"] = continent_name
    except Exception:
        row["continent"] = None

    return row
