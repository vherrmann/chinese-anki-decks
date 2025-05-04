from openai import OpenAI

client = OpenAI()


# https://platform.openai.com/docs/pricing
# https://platform.openai.com/usage

tokensTotal = 0
model = "gpt-4.1-mini"


def countTokens(func):
    def wrapper(*args, **kwargs):
        global tokensTotal
        completion = func(*args, **kwargs)
        tokens = completion.usage.total_tokens
        tokensTotal += tokens
        print(f"Used tokens: {tokens}")
        print(f"Used tokens total: {tokensTotal}")
        print(f"Est. total cost: {tokensTotal/1000000*40}ct")
        return completion

    return wrapper


# @countTokens
def askGPTJSON(msg, model=model, **kwargs):
    return client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a skilled chinese teacher, who only responds in machine-readable json without unnecessary characters like line breaks or whitespace.",
            },
            {"role": "user", "content": msg},
        ],
        **kwargs,
    )


# @countTokens
def askGPT(msg, model=model, **kwargs):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a skilled chinese teacher."},
            {"role": "user", "content": msg},
        ],
        **kwargs,
    )
