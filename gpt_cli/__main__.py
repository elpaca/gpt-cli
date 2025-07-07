#!/usr/bin/env python

SYSTEM_PROMPT = '''
你是一个运行在命令行环境中的助手，善于帮助用户解答问题。
【关于输出格式】
你的输出将直接展示在命令行中，因此不要输出markdown格式，输出纯文本格式。
不要使用 ** 表示加粗。
标题不要使用 ## ，可以使用【】等括号表示。
可使用 - 表示分层结构。
可使用 1. 2. 等序号格式。
'''

import os
import argparse

from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENAI_API_BASE"):
    client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_API_BASE"))
else:
    client = OpenAI(api_key=api_key)

def fetch_output(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True
    )
    answer = ""
    print()
    for chunk in response:
        content = chunk.choices[0].delta.content or ""
        print(content, end='', flush=True)
        answer += content
    print()
    print()
    return answer

def read_user_input():
    print(">>> ", end='', flush=True)
    line = ''
    try:
        line = input()
    except (EOFError, KeyboardInterrupt):
        pass

    return line

def main():
    parser = argparse.ArgumentParser(description="命令行大模型助手")
    parser.add_argument('question', nargs=argparse.REMAINDER, help='你的问题')
    args = parser.parse_args()

    if args.question:
        question = ' '.join(args.question)
    else:
        question = read_user_input()

    if not question.strip():
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    while True:
        try:
            answer = fetch_output(messages)
        except KeyboardInterrupt:
            break
        messages.append({"role": "assistant", "content": answer})
        followup = read_user_input()
        if not followup.strip():
            break
        messages.append({"role": "user", "content": followup})

if __name__ == "__main__":
    main()
