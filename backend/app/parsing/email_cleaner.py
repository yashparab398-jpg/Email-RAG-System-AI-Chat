import re


def remove_reply_trail(text):

    if not text:

        return ""

    patterns = [
        r"-----Original Message-----",
        r"From:",
        r"Sent:",
        r"To:",
        r"Subject:"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            text = text[:match.start()]

    return text


def remove_signature(text):

    if not text:

        return ""

    signature_markers = [
        "-- ",
        "Regards,",
        "Thanks,"
    ]

    for marker in signature_markers:

        if marker in text:

            text = text.split(marker)[0]

    return text


def normalize_whitespace(text):

    if not text:

        return ""

    return " ".join(text.split())


def clean_email(text):

    text = remove_reply_trail(text)

    text = remove_signature(text)

    text = normalize_whitespace(text)

    return text