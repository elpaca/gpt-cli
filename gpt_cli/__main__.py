#!/usr/bin/env python

SYSTEM_PROMPT = '''
你是一个运行在命令行环境中的助手，善于帮助用户解答问题。
【关于输出格式】
你的输出将直接展示在命令行中，因此输出纯文本格式，不要输出markdown格式。
不要使用 * 或 ** 表示斜体、加粗。
不要使用 ## 表示标题，可以使用【】方括号表示。
其他的markdown语法，如 - 表示分层结构， 1. 2. 等序号格式仍可正常使用。
'''

import os
import argparse

from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENAI_API_BASE"):
    client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_API_BASE"))
else:
    client = OpenAI(api_key=api_key)

multiline = False
multiline_eof = False
model_name = "deepseek-chat"

def fetch_output(messages):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True
    )
    answer = ""
    if not multiline:
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
    try:
        if multiline or multiline_eof:
            lines = []
            try:
                while True:
                    line = input()
                    if not multiline_eof and line == '':
                        break
                    lines.append(line)
            except EOFError:
                pass
            return '\n'.join(lines)
        else:
            line = ''
            try:
                line = input()
            except EOFError:
                pass
            return line
    except KeyboardInterrupt:
        return ''

def main():
    parser = argparse.ArgumentParser(description="命令行大模型助手")
    parser.add_argument('-m', '--multiline', action='store_true', help='允许多行输入（默认单行），使用空行结束输入')
    parser.add_argument('-e', '--multiline-eof', action='store_true', help='允许多行输入，使用EOF（Ctrl+Z，Windows/Ctrl+Z，Unix）结束输入')
    parser.add_argument('--model', default='deepseek-chat', help='使用的模型名称')
    parser.add_argument('question', nargs=argparse.REMAINDER, help='你的问题')
    args = parser.parse_args()

    global multiline, multiline_eof, model_name
    multiline = args.multiline
    multiline_eof = args.multiline_eof
    model_name = args.model

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

        if args.question:
            break # single turn
        
        messages.append({"role": "assistant", "content": answer})
        followup = read_user_input()
        if not followup.strip():
            break
        messages.append({"role": "user", "content": followup})

if __name__ == "__main__":
    main()
