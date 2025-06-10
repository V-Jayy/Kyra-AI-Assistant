import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from assistant.nlu import classify


def test_nlu_classify_open_website():
    intent, args, conf = classify("please open youtube")
    assert intent == "open_website"
    assert args.get("url") == "youtube.com"
    assert conf >= 0.75
