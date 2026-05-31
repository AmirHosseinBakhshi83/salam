from django import template

register = template.Library()

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.simple_tag
def zip_with_letters(list1, list2):
    """Return zipped list with Persian letters"""
    letters = {1: 'الف', 2: 'ب', 3: 'ج', 4: 'د', 5: 'ه'}
    result = []
    for i, (item1, item2) in enumerate(zip(list1, list2), start=1):
        result.append({
            'letter': letters.get(i, str(i)),
            'index': i,
            'correct': item1,
            'user_answer': item2
        })
    return result
