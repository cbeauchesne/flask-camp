import collections

from flask import current_app

from wiki_api.services.security import allow

rule = "/"


@allow("anonymous", "authenticated", allow_blocked=True)
def get():
    """Display the possible route for this API"""

    site_map = collections.defaultdict(dict)

    for url_rule in current_app.url_map.iter_rules():
        for method in url_rule.methods:
            if method not in ["OPTIONS", "HEAD"]:
                view_func = current_app.view_functions.get(url_rule.endpoint, None)
                doc = "" if view_func is None else view_func.__doc__
                site_map[url_rule.rule][method] = {"description": doc}

                if url_rule.rule in current_app._rate_limits and method in current_app._rate_limits[url_rule.rule]:
                    site_map[url_rule.rule][method]["rate_limit"] = current_app._rate_limits[url_rule.rule][method]

                if hasattr(view_func, "allowed_roles"):
                    site_map[url_rule.rule][method]["allowed_roles"] = list(view_func.allowed_roles)

                if hasattr(view_func, "allow_blocked"):
                    site_map[url_rule.rule][method]["allow_blocked"] = view_func.allow_blocked

    return site_map
