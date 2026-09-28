from attacks.scoring import AttackCase, Score, score_response


def score_pyrit_response(case: AttackCase, response: str, fake_secret: str) -> Score:
    """Use the shared lab scoring contract for PyRIT responses."""

    return score_response(case, response, fake_secret)
