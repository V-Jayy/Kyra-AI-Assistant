import os, sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_kill_process(monkeypatch):
    called = {}

    def fake_run(cmd, check):
        called['cmd'] = cmd
        return None

    monkeypatch.setattr(subprocess, 'run', fake_run)
    ok, msg = tools.kill_process('discord')
    assert ok
    assert 'discord' in msg.lower()
    if os.name == 'nt':
        assert called['cmd'] == ['taskkill', '/F', '/IM', 'discord.exe']
    else:
        assert called['cmd'] == ['pkill', '-f', 'discord']
