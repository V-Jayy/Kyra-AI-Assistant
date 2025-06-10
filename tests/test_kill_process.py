import os, sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_kill_process(monkeypatch):
    called = {}

    def fake_run(cmd, check, stdout=None, stderr=None):
        called['cmd'] = cmd
        class Result:
            pass
        return Result()

    monkeypatch.setattr(subprocess, 'run', fake_run)
    ok, msg = tools.kill_process('discord')
    assert ok
    assert 'discord' in msg.lower()
    if os.name == 'nt':
        assert called['cmd'][0].lower() == 'taskkill'
        assert called['cmd'][3].lower() == 'discord.exe'
    else:
        assert called['cmd'][0] == 'pkill'
        assert called['cmd'][2] == 'discord'
