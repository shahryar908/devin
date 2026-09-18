import random
import string

OPS = {
    "add": ("+", lambda a, b: a + b),
    "sub": ("-", lambda a, b: a - b),
    "mul": ("*", lambda a, b: a * b),
    "div": ("/", lambda a, b: a // b),
}

DIFFICULTY_RANGES = {
    "easy":   {"add": (1, 10), "sub": (1, 10)},
    "medium": {"add": (10, 50), "sub": (10, 50), "mul": (2, 12)},
    "hard":   {"add": (50, 200), "sub": (50, 200), "mul": (3, 15), "div": (2, 15)},
}
DIFFICULTIES = {"easy", "medium", "hard"}


class Question:
    def __init__(self, question_id: str, prompt: str, answer: int, options: list[int]):
        self.id = question_id
        self.prompt = prompt
        self.answer = answer
        self.options = options

    def client_payload(self) -> dict:
        return {
            "questionId": self.id,
            "prompt": self.prompt,
            "answerOptions": self.options,
        }


def _pick_operands(op: str, lo: int, hi: int) -> tuple[int, int]:
    a = random.randint(lo, hi)
    b = random.randint(lo, hi)
    if op == "sub":
        return (max(a, b), min(a, b))
    if op == "div":
        b = max(b, 1)
        a = b * random.randint(2, max(hi // b, 2))
    return (a, b)


def generate_question(difficulty: str, used: set[str], qid_counter: list[int]) -> Question | None:
    ranges = DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["medium"])
    attempts = 0
    while attempts < 50:
        op = random.choice(list(ranges.keys()))
        lo, hi = ranges[op]
        a, b = _pick_operands(op, lo, hi)
        symbol, fn = OPS[op]
        answer = fn(a, b)
        expr = f"{a}{symbol}{b}"
        if expr in used:
            attempts += 1
            continue

        used.add(expr)
        qid_counter[0] += 1
        question_id = f"{qid_counter[0]:04d}"
        options = {answer}
        span = max(5, answer // 2)
        while len(options) < 4:
            options.add(max(0, answer + random.randint(-span, span)))
        return Question(question_id, f"{a} {symbol} {b} = ?", answer, list(options))
    return None


def room_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))