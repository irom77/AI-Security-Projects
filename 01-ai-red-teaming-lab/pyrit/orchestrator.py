import base64
import codecs
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from attacks.scoring import AttackCase
from pyrit.scorers import score_pyrit_response


def _base64(prompt: str) -> str:
    return base64.b64encode(prompt.encode()).decode()


def _rot13(prompt: str) -> str:
    return codecs.encode(prompt, "rot_13")


def _letter_by_letter(prompt: str) -> str:
    return " ".join(prompt)


CONVERTERS: dict[str, Callable[[str], str]] = {
    "base64": _base64,
    "rot13": _rot13,
    "letter_by_letter": _letter_by_letter,
}


@dataclass
class Orchestrator:
    target: Any
    cases: list[AttackCase]
    converters: list[str]
    scorers: list[str]

    def run(self, fake_secret: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for case in sorted(self.cases, key=lambda item: item.id):
            for converter_name in ["identity", *self.converters]:
                if converter_name == "identity":
                    prompt = case.prompt
                    lineage: list[str] = []
                else:
                    try:
                        prompt = CONVERTERS[converter_name](case.prompt)
                    except KeyError as exc:
                        raise ValueError(f"unsupported converter: {converter_name}") from exc
                    lineage = [converter_name]
                response = self.target.send(prompt)
                score = score_pyrit_response(case, response, fake_secret)
                results.append(
                    {
                        "tool": "pyrit",
                        "attack_case_id": case.id,
                        "prompt": prompt,
                        "response": response,
                        "converter": converter_name,
                        "converter_lineage": lineage,
                        "score": score,
                    }
                )
        return results


def build_attack_orchestrator(target: Any, cases: Iterable[AttackCase], converters: list[str], scorers: list[str]) -> Orchestrator:
    return Orchestrator(target, list(cases), list(converters), list(scorers))
