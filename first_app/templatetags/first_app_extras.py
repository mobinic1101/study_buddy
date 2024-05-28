from django import template


register = template.Library()

register.filter("get_dict_value", lambda dictionary, val: dictionary.get(val, ""))
