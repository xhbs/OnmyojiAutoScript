# This Python file uses the following encoding: utf-8

import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from module.logger import logger


class TemplateManager(QObject):
    """Persist reusable sets of task names for the GUI shortcut."""

    templates_changed = Signal()

    path = Path.cwd() / "config" / "templates.json"

    def __init__(self) -> None:
        super().__init__()

    def _read(self) -> dict[str, list[str]]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            logger.error(f"Read task templates failed: {error}")
            return {}

        if not isinstance(data, dict):
            return {}
        return {
            str(name): [str(task) for task in tasks if str(task).strip()]
            for name, tasks in data.items()
            if isinstance(tasks, list) and str(name).strip()
        }

    def _write(self, data: dict[str, list[str]]) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            self.templates_changed.emit()
            return True
        except OSError as error:
            logger.error(f"Write task templates failed: {error}")
            return False

    @Slot(result="QString")
    def list_templates(self) -> str:
        """Return templates as a JSON array for QML."""
        return json.dumps(
            [
                {
                    "name": name,
                    "tasks_json": json.dumps(tasks, ensure_ascii=False),
                }
                for name, tasks in self._read().items()
            ],
            ensure_ascii=False,
        )

    @Slot(str, str, result="bool")
    def save_template(self, name: str, tasks: str) -> bool:
        name = str(name or "").strip()
        if not name:
            return False
        try:
            task_names = json.loads(tasks) if isinstance(tasks, str) else tasks
        except (TypeError, json.JSONDecodeError):
            return False
        if not isinstance(task_names, list) or not task_names:
            return False

        unique_tasks = []
        for task_name in task_names:
            task_name = str(task_name).strip()
            if task_name and task_name not in unique_tasks:
                unique_tasks.append(task_name)

        data = self._read()
        data[name] = unique_tasks
        return self._write(data)

    @Slot(str, result="bool")
    def delete_template(self, name: str) -> bool:
        name = str(name or "").strip()
        data = self._read()
        if name not in data:
            return False
        del data[name]
        return self._write(data)
