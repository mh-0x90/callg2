from __future__ import annotations

from django.contrib.auth.decorators import user_passes_test


def is_operator(user) -> bool:
    return user.is_authenticated and user.groups.filter(name="operator").exists()


operator_required = user_passes_test(is_operator)