from django import template
from datetime import date

register = template.Library()


@register.filter
def is_overdue(due_date):
    """Check if a due date is in the past."""
    if due_date is None:
        return False
    return due_date < date.today()


@register.filter
def is_today(due_date):
    """Check if a due date is today."""
    if due_date is None:
        return False
    return due_date == date.today()

