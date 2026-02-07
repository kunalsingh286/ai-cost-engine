import tiktoken


def count_tokens(text: str, model: str) -> int:

    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")

    tokens = enc.encode(text)

    return len(tokens)
