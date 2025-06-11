import os, sys, shutil, subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_install_and_uninstall_cmd(monkeypatch, tmp_path):
    target = tmp_path / "Program Files" / "Kyra"
    launcher = tmp_path / "Windows" / "Kyra.bat"
    monkeypatch.setenv("KYRA_INSTALL_DIR", str(target))
    monkeypatch.setenv("KYRA_LAUNCHER_PATH", str(launcher))
    monkeypatch.setattr(tools.os, "name", "nt")

    monkeypatch.setattr(shutil, 'copytree', lambda src, dst, dirs_exist_ok=True: None)

    calls = []
    monkeypatch.setattr(subprocess, 'check_call', lambda cmd: calls.append(cmd))

    ok, msg = tools.install_cmd()
    assert ok
    assert launcher.exists()
    assert target.exists()
    content = launcher.read_text()
    assert 'app.assistant' in content

    ok2, msg2 = tools.uninstall_cmd()
    assert ok2
    assert not launcher.exists()
