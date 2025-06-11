import os, sys, shutil, types, tempfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_install_and_uninstall_cmd(monkeypatch, tmp_path):
    path_dir = tmp_path / "bin"
    path_dir.mkdir()
    monkeypatch.setenv("PATH", str(path_dir))

    # avoid copying the whole repo in tests
    monkeypatch.setattr(shutil, 'copytree', lambda src, dst, dirs_exist_ok=True: None)

    ok, msg = tools.install_cmd()
    assert ok
    script = path_dir / ("Kyra.cmd" if os.name == 'nt' else "Kyra")
    assert script.exists()
    content = script.read_text()
    assert 'app.assistant' in content

    ok2, msg2 = tools.uninstall_cmd()
    assert ok2
    assert not script.exists()
