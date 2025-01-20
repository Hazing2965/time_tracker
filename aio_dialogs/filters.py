import regex


def action_check(text: str) -> str:
    pattern = regex.compile(r'^[\p{L}\p{N}\s!"#$%&\'()*+,-./:;<=>?@[\\\]^_`{|}~]*$', regex.UNICODE)
    if (bool(pattern.match(text))) is False:
        raise ValueError('emoji')
    elif len(text) <= 20:
        return text
    else:
        raise ValueError
