import json

from module.config.task_templates import TaskTemplateStore, build_task_template_tasks


class FakeConfigModel:
    @staticmethod
    def dict():
        return {
            "config_name": "oas1",
            "restart": {},
            "script": {"error": {}},
            "area_boss": {"scheduler": {"enable": True}},
            "pets": {"scheduler": {"enable": False}},
        }

    @staticmethod
    def type(key):
        return {"area_boss": "AreaBoss", "pets": "Pets"}[key]


class FakeConfig:
    model = FakeConfigModel()


def test_task_template_store_save_rename_and_delete(tmp_path):
    path = tmp_path / "templates.json"
    store = TaskTemplateStore(path)

    assert store.save_template("日常", ["DailyTrifles", "DailyTrifles", "Pets"])
    assert store.list_templates() == [
        {"name": "日常", "tasks": ["DailyTrifles", "Pets"]}
    ]

    assert store.save_template("每日", ["AreaBoss"], previous_name="日常")
    assert store.get_template("日常") is None
    assert store.get_template("每日") == ["AreaBoss"]

    assert store.delete_template("每日")
    assert json.loads(path.read_text(encoding="utf-8")) == {}


def test_task_template_store_rejects_empty_values(tmp_path):
    store = TaskTemplateStore(tmp_path / "templates.json")

    assert not store.save_template("", ["Pets"])
    assert not store.save_template("日常", [])
    assert store.list_templates() == []


def test_build_task_template_tasks_from_base_config_model():
    assert build_task_template_tasks(FakeConfig()) == [
        {"name": "AreaBoss", "enabled": True},
        {"name": "Pets", "enabled": False},
    ]
