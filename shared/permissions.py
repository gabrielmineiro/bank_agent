from functools import wraps

PRIVILEGED_ROLES = {"manager", "admin"}

ROLE_PERMISSIONS = {
    "customer": {
        "data_scope": "own",
        "description": "Pode consultar e operar apenas seus próprios dados.",
    },
    "manager": {
        "data_scope": "global",
        "description": "Pode consultar dados e alterar limites de qualquer cliente.",
    },
    "admin": {
        "data_scope": "global",
        "description": "Acesso total ao sistema.",
    },
}


def _can_access_customer_data(role: str, logged_user_id: str, target_customer_id: str) -> bool:
    """
    Returns True if the authenticated user is allowed to access the target customer's data.

    Rules:
    - Privileged roles (manager, admin): global scope — can access any customer.
    - All other roles (customer): own scope — can only access their own data.
    """
    if role in PRIVILEGED_ROLES:
        return True
    return logged_user_id == target_customer_id



def require_access(deny_msg: str):
    """Decorator that enforces RBAC. Expects (role, user_id, customer_id, ...) signature."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(role: str, user_id: str, customer_id: str, *args, **kwargs):
            if not _can_access_customer_data(role, user_id, customer_id):
                return f"Acesso negado: {deny_msg}"
            return fn(role, user_id, customer_id, *args, **kwargs)
        return wrapper
    return decorator
