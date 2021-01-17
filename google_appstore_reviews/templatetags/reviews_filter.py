from django import template

register = template.Library()


@register.filter
def platform_filter(platform: str):
    if platform.lower() == 'android':
        return 'Google Play'
    elif platform.lower() == 'ios':
        return 'App Store'
    else:
        return platform.title()

@register.filter
def country_filter(country: str):
    country_mapping = {
        'us': 'United States',
        'au': 'Australia',
        'ph': 'Philippines',
        'fr': 'France',
        'tw': 'China taiwan',
        'es': 'Spain',
        'it': 'Italy',
        'cd': 'Canada',
        'de': 'Germany',
        'br': 'Brazil',
    }
    country_fullname = country_mapping.get(country, None)
    if country_fullname is None:
        return country
    else:
        return country_fullname


@register.filter
def select_transform_filter(select: str):
    if select == '*':
        return 'All'
    return select
