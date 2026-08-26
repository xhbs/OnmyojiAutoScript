# This Python file uses the following encoding: utf-8

import json

from PySide6.QtCore import QObject, Signal, Slot

from module.config.task_templates import TaskTemplateStore


class TemplateManager(QObject):
    """Persist reusable sets of task names for the GUI shortcut."""

    templates_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.store = TaskTemplateStore()

    @Slot(result="QString")
    def list_templates(self) -> str:
        """Return templates as a JSON array for QML."""
        return json.dumps(
            [
                {
                    "name": item["name"],
                    "tasks_json": json.dumps(item["tasks"], ensure_ascii=False),
                }
                for item in self.store.list_templates()
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

        saved = self.store.save_template(name, task_names)
        if saved:
            self.templates_changed.emit()
        return saved

    @Slot(str, result="bool")
    def delete_template(self, name: str) -> bool:
        deleted = self.store.delete_template(name)
        if deleted:
            self.templates_changed.emit()
        return deleted
