def action_check(text: str) -> str:
    if len(text) <= 15:

        return text
    else:
        raise ValueError