from django import template

register = template.Library()


@register.filter
def unpack_dict(dict_: dict):
    res = []
    for k, v in dict_.items():
        res.append((k, v))
    print(res)
    return res

