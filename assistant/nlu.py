import os
import re
import yaml
import joblib
from typing import Any, Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from rapidfuzz import fuzz
from pathlib import Path

# path to filler words file used for basic text normalisation
FILLER_FILE = Path(__file__).with_name("filler_words.txt")


def normalize(text: str) -> str:
    """Lowercase and strip filler words from the input."""
    if FILLER_FILE.exists():
        with open(FILLER_FILE, "r", encoding="utf-8") as f:
            fillers = [re.escape(w.strip()) for w in f if w.strip()]
        if fillers:
            pattern = re.compile(r"\b(?:" + "|".join(fillers) + r")\b", re.I)
            text = pattern.sub("", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


class Command:
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.phrases = data.get('phrases', [])
        self.slots = {name: re.compile(pattern, re.I) for name, pattern in data.get('slots', {}).items()}
        self.action = data['action']
        self.args = data.get('args', {})


class NLU:
    def __init__(self, commands: List[Command], model_path: str = 'nlu.joblib'):
        self.commands = commands
        self.model_path = model_path
        texts = []
        labels = []
        for cmd in commands:
            for p in cmd.phrases:
                # replace slot markers with the slot name so the model can generalise
                processed = re.sub(r"{(\w+)}", r"\1", p)
                texts.append(processed)
                labels.append(cmd.id)
        if os.path.exists(model_path):
            self.vectorizer, self.clf = joblib.load(model_path)
        else:
            self.vectorizer = TfidfVectorizer()
            X = self.vectorizer.fit_transform(texts)
            self.clf = LogisticRegression(max_iter=200)
            self.clf.fit(X, labels)
            joblib.dump((self.vectorizer, self.clf), model_path)

    def _extract_slots(self, text: str, command: Command) -> Dict[str, str]:
        slots = {}
        for name, pattern in command.slots.items():
            m = pattern.search(text)
            if m:
                slots[name] = m.group(0)
        return slots

    def predict(self, text: str) -> Tuple[str, Dict[str, str], float]:
        X = self.vectorizer.transform([text])
        probs = self.clf.predict_proba(X)[0]
        idx = probs.argmax()
        intent = self.clf.classes_[idx]
        conf = float(probs[idx])
        command = next((c for c in self.commands if c.id == intent), None)
        slots: Dict[str, str] = {}
        if command:
            slots = self._extract_slots(text, command)
        if conf < 0.6:
            intent, slots, conf = self.fuzzy_fallback(text)
        return intent, slots, conf

    def fuzzy_fallback(self, text: str) -> Tuple[str, Dict[str, str], float]:
        best_cmd = None
        best_score = 0
        for cmd in self.commands:
            for p in cmd.phrases:
                score = fuzz.ratio(text.lower(), p.lower()) / 100.0
                if score > best_score:
                    best_score = score
                    best_cmd = cmd
        if best_cmd and best_score >= 0.5:
            slots = self._extract_slots(text, best_cmd)
            return best_cmd.id, slots, best_score
        return "", {}, best_score


def load_commands(path: str) -> List[Command]:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return [Command(item) for item in data]
