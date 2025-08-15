from django import template

register = template.Library()


@register.filter
def replace(value: str, arg: str) -> str:
    old, new = arg.split(",")

    return value.replace(old, new)
