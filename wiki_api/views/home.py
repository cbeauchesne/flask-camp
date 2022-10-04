import collections

from flask import current_app

rule = "/"


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

    return site_map