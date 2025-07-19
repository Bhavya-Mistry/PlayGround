# import ollama

# def ask(question):
#     response = ollama.chat(
#         model='phi3',
#         messages=[{"role":"user", "content":question}],
#         stream=True
#     )
#     return response['message']['content']


# while True:
#     userinput = input("You:")

#     if userinput.lower() in ['exit', 'quit']:
#         break

#     answer = ask(userinput)
#     # for chunk in stream:
#     # print(chunk['message']['content'], end='', flush=True)
#     print("Path Pilot: ", answer)


import ollama

def ask(question):
    stream = ollama.chat(
        model='phi3',
        messages=[{"role": "user", "content": question}],
        stream=True,
        options={"temperature":0.8}
    )
    print("Path Pilot: ", end='', flush=True)
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
    print()  # For new line after response

# Loop
while True:
    userinput = input("You: ")
    if userinput.lower() in ['exit', 'quit']:
        break
    ask(userinput)
