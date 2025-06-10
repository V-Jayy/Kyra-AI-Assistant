import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from assistant.nlu import load_commands, NLU
import os


def test_nlu_predict(tmp_path):
    commands = load_commands(os.path.join(os.path.dirname(__file__), '../assistant/commands.yml'))
    nlu = NLU(commands, model_path=tmp_path/'model.joblib')
    intent, slots, conf = nlu.predict('open google')
    assert intent
    assert conf > 0.0
