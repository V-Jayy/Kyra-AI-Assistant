import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from assistant.router import Router
from assistant import actions


def test_router_polite_phrases(tmp_path):
    # create minimal capabilities for router
    Router()  # ensure capabilities.json exists via actions import
    caps = tmp_path / 'cap.json'
    with open('capabilities.json', 'r', encoding='utf-8') as f_in:
        data = json.load(f_in)
    with open(caps, 'w', encoding='utf-8') as f_out:
        json.dump(data, f_out)

    router = Router(capabilities_path=str(caps), model_path=None)
    fn, kwargs = router.select('Could you kindly open YouTube?')
    assert fn == actions.open_website
    assert 'youtube' in kwargs.get('url', '')

    fn2, kwargs2 = router.select('Show me my downloads, please')
    assert fn2 == actions.reveal_folder

