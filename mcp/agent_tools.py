import inspect

from langchain_core.tools import StructuredTool

from mcp.priviled_tools import PRIVILEGED_TOOLS
from mcp.base_tools import BASE_TOOLS
from shared.permissions import PRIVILEGED_ROLES


def _bind_auth(fn, role: str, user_id: str):
    """
    Returns a *real* function with `role` and `user_id` pre-bound, exposing
    only the remaining parameters (e.g. customer_id, amount, …) to LangChain.

    Why not functools.partial?
    ──────────────────────────
    StructuredTool.from_function calls Pydantic's validate_arguments, which in
    turn calls typing.get_type_hints(obj). That function requires a true Python
    function/method/class — functools.partial objects are rejected with:
        TypeError: functools.partial(...) is not a module, class, method, or function.

    By setting __signature__ and __annotations__ on the inner wrapper we give
    Pydantic exactly what it needs to build the correct JSON schema, while still
    keeping role/user_id invisible to the LLM.
    """
    sig = inspect.signature(fn)
    remaining_params = [
        p for p in sig.parameters.values()
        if p.name not in ("role", "user_id")
    ]

    def wrapper(*args, **kwargs):
        return fn(role, user_id, *args, **kwargs)

    clean_hints = {
        k: v for k, v in fn.__annotations__.items()
        if k not in ("role", "user_id")
    }

    wrapper.__name__ = fn.__name__
    wrapper.__qualname__ = fn.__qualname__
    wrapper.__doc__ = fn.__doc__
    wrapper.__module__ = fn.__module__
    wrapper.__annotations__ = clean_hints
    wrapper.__signature__ = sig.replace(parameters=remaining_params)

    return wrapper


def create_tools_for_user(user_id: str, role: str) -> list:
    """
    Builds LangChain tools with auth context bound at session creation time.

    Security model:
    - user_id and role are bound once and hidden from the LLM.
    - Tools marked with auth=True enforce per-record ownership checks.
    - Privileged tools are only included for manager/admin roles.
    """
    defs = list(BASE_TOOLS)
    if role in PRIVILEGED_ROLES:
        defs.extend(PRIVILEGED_TOOLS)

    tools = []
    for d in defs:
        func = _bind_auth(d["func"], role, user_id) if d["auth"] else d["func"]
        tools.append(StructuredTool.from_function(
            func=func, name=d["name"], description=d["description"],
        ))
    return tools