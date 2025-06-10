import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from assistant.tools import match_tool
import assistant.actions  # register tools

commands = {
    "open youtube": "open_website",
    "launch youtube dot com": "open_website",
    "go to reddit.com": "open_website",
    "open the website example.com": "open_website",
    "please open https://google.com": "open_website",
    "launch chrome": "launch_app",
    "open firefox": "launch_app",
    "start notepad": "launch_app",
    "open application calculator": "launch_app",
    "launch vscode": "launch_app",
    "search for report in downloads": "search_files",
    "search for invoice.pdf in documents": "search_files",
    "find notes.txt in home": "search_files",
    "search for *.py in projects folder": "search_files",
    "look for todo in desktop": "search_files",
    "open downloads folder": "reveal_folder",
    "show me my documents": "reveal_folder",
    "reveal pictures directory": "reveal_folder",
    "open the folder music": "reveal_folder",
    "show my downloads": "reveal_folder",
}


def test_match_tool_paraphrases():
    for text, expected in commands.items():
        tool, _ = match_tool(text)
        assert tool is not None, text
        assert tool.name == expected
