
def fmt_history(history: list[list[str]]) -> str:
    return "\n".join([f"Chat: {x[0]}\nUser:{x[1]}\n\n" for x in history])
