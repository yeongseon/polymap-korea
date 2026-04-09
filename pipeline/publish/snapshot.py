from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import TypeVar, cast

FlowFunction = TypeVar("FlowFunction", bound=Callable[..., dict[str, str]])


def flow(name: str) -> Callable[[FlowFunction], FlowFunction]:
    try:
        prefect_module = import_module("prefect")
    except ModuleNotFoundError:
        def decorator(func: FlowFunction) -> FlowFunction:
            return func

        return decorator
    prefect_flow = cast(Callable[[str], Callable[[FlowFunction], FlowFunction]], prefect_module.flow)
    return prefect_flow(name)


@flow(name="publish-snapshot")
def publish_snapshot_flow() -> dict[str, str]:
    return {
        "status": "ready",
        "target": "postgresql",
    }
