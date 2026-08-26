# This Python file uses the following encoding: utf-8

import json
from pathlib import Path
from threading import RLock

from module.logger import logger


class TaskTemplateStore:
    """Persist reusable task selections independently from any GUI toolkit."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path.cwd() / "config" / "templates.json"
        self._lock = RLock()

    @staticmethod
    def _normalize_tasks(tasks) -> list[str]:
        if not isinstance(tasks, list):
            return []

        normalized = []
        for task in tasks:
            task_name = str(task).strip()
            if task_name and task_name not in normalized:
                normalized.append(task_name)
        return normalized

    def _read_unlocked(self) -> dict[str, list[str]]:
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
            str(name).strip(): self._normalize_tasks(tasks)
            for name, tasks in data.items()
            if str(name).strip() and isinstance(tasks, list)
        }

    def _write_unlocked(self, data: dict[str, list[str]]) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except OSError as error:
            logger.error(f"Write task templates failed: {error}")
            return False

    def list_templates(self) -> list[dict[str, object]]:
        with self._lock:
            return [
                {"name": name, "tasks": list(tasks)}
                for name, tasks in self._read_unlocked().items()
            ]

    def get_template(self, name: str) -> list[str] | None:
        template_name = str(name or "").strip()
        if not template_name:
            return None
        with self._lock:
            tasks = self._read_unlocked().get(template_name)
            return list(tasks) if tasks is not None else None

    def save_template(
        self,
        name: str,
        tasks: list[str],
        previous_name: str | None = None,
    ) -> bool:
        template_name = str(name or "").strip()
        task_names = self._normalize_tasks(tasks)
        if not template_name or not task_names:
            return False

        with self._lock:
            data = self._read_unlocked()
            old_name = str(previous_name or "").strip()
            if old_name and old_name != template_name:
                data.pop(old_name, None)
            data[template_name] = task_names
            return self._write_unlocked(data)

    def delete_template(self, name: str) -> bool:
        template_name = str(name or "").strip()
        with self._lock:
            data = self._read_unlocked()
            if template_name not in data:
                return False
            del data[template_name]
            return self._write_unlocked(data)
