# This Python file uses the following encoding: utf-8

import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from module.config.task_templates import TaskTemplateStore
from module.server.api_logger import ApiLoggingRoute
from module.server.main_manager import mm
from module.server.script_process import ScriptState


template_app = APIRouter(
    prefix="/task_templates",
    tags=["task templates"],
    route_class=ApiLoggingRoute,
)
template_store = TaskTemplateStore()


class TaskTemplatePayload(BaseModel):
    name: str
    tasks: list[str]
    previous_name: str | None = None


def _ensure_config(config_name: str):
    if config_name not in mm.all_script_files():
        raise HTTPException(status_code=404, detail=f"Config not found: {config_name}")
    return mm.config_cache(config_name)


@template_app.get("")
async def task_template_list():
    return template_store.list_templates()


@template_app.get("/tasks")
async def task_template_tasks(config_name: str = Query(...)):
    config = _ensure_config(config_name)
    task_data = json.loads(config.gui_task_list())
    return [
        {"name": name, "enabled": bool(value.get("enable", False))}
        for name, value in task_data.items()
    ]


@template_app.put("")
async def task_template_save(payload: TaskTemplatePayload):
    if not template_store.save_template(
        payload.name,
        payload.tasks,
        previous_name=payload.previous_name,
    ):
        raise HTTPException(
            status_code=400,
            detail="Template name and at least one task are required",
        )
    return {"saved": True, "name": payload.name.strip()}


@template_app.delete("/{name}")
async def task_template_delete(name: str):
    if not template_store.delete_template(name):
        raise HTTPException(status_code=404, detail=f"Template not found: {name}")
    return {"deleted": True, "name": name}


@template_app.post("/{name}/apply")
async def task_template_apply(name: str, config_name: str = Query(...)):
    tasks = template_store.get_template(name)
    if tasks is None:
        raise HTTPException(status_code=404, detail=f"Template not found: {name}")

    script_process = mm.script_process.get(config_name)
    if script_process is None:
        raise HTTPException(status_code=404, detail=f"Config not found: {config_name}")
    if script_process.state != ScriptState.INACTIVE:
        raise HTTPException(
            status_code=409,
            detail="Stop the script before applying a task template",
        )

    config = _ensure_config(config_name)
    if not config.apply_task_template(tasks):
        raise HTTPException(
            status_code=400,
            detail="Template does not contain tasks available in this config",
        )

    config.get_next()
    await script_process.broadcast_state({"schedule": config.get_schedule_data()})
    return {"applied": True, "name": name, "config_name": config_name}
