import locale

from jinja2 import Environment

from django.templatetags.static import static
from django.urls import reverse

import core



# Set the locale to Italian
locale.setlocale(locale.LC_ALL, 'it_IT.utf8')


def format_italian(num):
    try:
        return locale.format_string("%d", num, grouping=True)
    except (TypeError, ValueError):
        return num


def jinja_url(viewname, *args, **kwargs):
    return reverse(viewname, args=args, kwargs=kwargs)


class JinjaEnvironment(Environment):
    def __init__(self, **kwargs):
        super(JinjaEnvironment, self).__init__(**kwargs)

        self.globals.update({
            'static': static,
            'url': reverse,
            # 'get_all_urls_starting_with': core.utils.get_all_urls_starting_with,
            'myurl': jinja_url,
        })

        self.filters['format_italian'] = format_italian


