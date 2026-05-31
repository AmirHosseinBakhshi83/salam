from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    return form[field_name]

@register.filter
def answer_field(form, question):
    field_name = f"answer_{question.id}"
    return form[field_name]