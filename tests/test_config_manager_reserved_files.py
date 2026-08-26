from module.server.config_manager import ConfigManager, ConfigNameError


def _write_json(path, content="{}"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_template_store_is_not_listed_as_script_config(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    _write_json(config_dir / "template.json")
    _write_json(config_dir / "oas1.json")
    _write_json(config_dir / "templates.json")
    monkeypatch.chdir(tmp_path)

    assert ConfigManager.all_script_files() == ["oas1"]
    assert ConfigManager.all_json_file() == ["template", "oas1"]


def test_template_store_cannot_be_deleted_or_renamed(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    template_store = config_dir / "templates.json"
    config_file = config_dir / "oas1.json"
    _write_json(template_store)
    _write_json(config_file)
    monkeypatch.chdir(tmp_path)

    assert not ConfigManager.delete("templates")
    assert not ConfigManager.rename("templates", "removed")
    assert not ConfigManager.rename("oas1", "templates")
    assert template_store.exists()
    assert config_file.exists()


def test_template_store_name_is_reserved_for_imports():
    try:
        ConfigManager.validate_config_name("Templates", allow_template=False)
    except ConfigNameError:
        pass
    else:
        raise AssertionError("Templates must remain a reserved config name")
