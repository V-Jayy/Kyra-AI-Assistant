import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from assistant.router import Router
from assistant import actions


def test_router_polite_phrases():
    router = Router()
    fn, kwargs, intent, conf = router.select('Could you kindly open YouTube?')
    assert fn is not None
    assert fn.__name__ == actions.open_website.__name__
    assert kwargs.get('url') == 'youtube.com'
    assert intent == 'open_website'
    assert conf >= 0.75

    fn2, kwargs2, intent2, _ = router.select('Show me my downloads, please')
    assert fn2 is not None
    assert fn2.__name__ == actions.reveal_folder.__name__
    assert intent2 == 'reveal_folder'
