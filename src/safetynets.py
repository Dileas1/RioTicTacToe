from collections.abc import Callable
from typing import TypeVar, Any

T = TypeVar('T')

def noexcept(default: T) -> Callable[..., Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> T:
            try:
                return func(*args, **kwargs)
            except:
                return default
        return wrapper
    return decorator
