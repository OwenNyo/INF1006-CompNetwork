import openai
import socket
import threading
import time
import sys
import random

openai.api_key = 'sk-proj-FWxur14EgYq0dOKYyAPzT3BlbkFJBjC1j4krHEgw5CU7RqmC'

# Constants
HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 2048

BOT_NAME = ""
initial_prompt_sent = False

print_lock = threading.Lock()
typing_buffer = ""

ADJACENT_KEYS = {
    'q': ['w', 'a'],
    'w': ['q', 'e', 's'],
    'e': ['w', 'r', 'd'],
    'r': ['e', 't', 'f'],
    't': ['r', 'y', 'g'],
    'y': ['t', 'u', 'h'],
    'u': ['y', 'i', 'j'],
    'i': ['u', 'o', 'k'],
    'o': ['i', 'p', 'l'],
    'p': ['o', '[', ';'],
    'a': ['q', 's', 'z'],
    's': ['a', 'd', 'x'],
    'd': ['s', 'f', 'c'],
    'f': ['d', 'g', 'v'],
    'g': ['f', 'h', 'b'],
    'h': ['g', 'j', 'n'],
    'j': ['h', 'k', 'm'],
    'k': ['j', 'l', ','],
    'l': ['k', ';', '.'],
    'z': ['a', 'x'],
    'x': ['z', 'c'],
    'c': ['x', 'v'],
    'v': ['c', 'b'],
    'b': ['v', 'n'],
    'n': ['b', 'm'],
    'm': ['n', ',', '.'],
    ',': ['m', '.', '/'],
    '.': [',', '/', ';'],
    ';': ['l', '\'', '/'],
    '\'': [';', '/', '['],
    '[': ['p', ']', '\''],
    ']': ['[', '\\', '='],
    '\\': [']', '=', '-'],
    '1': ['2'],
    '2': ['1', '3'],
    '3': ['2', '4'],
    '4': ['3', '5'],
    '5': ['4', '6'],
    '6': ['5', '7'],
    '7': ['6', '8'],
    '8': ['7', '9'],
    '9': ['8', '0'],
    '0': ['9', '-', '='],
    '-': ['0', '=', '['],
    '=': ['-', '[', ']'],
    '/': ['.', ';'],
    '\'': [';', '.'],
}

# few-shot prompting
few_shot_prompts = [
    {"role": "user", "content": "eh bro, the other day i go try south canteen chicken rice not bad"},
    {"role": "assistant", "content": "really ah? where else food nice in school?"},
    {"role": "user", "content": "koufu mala not bad also"},
    {"role": "assistant", "content": "i see, ok next time try"},
    {"role": "user", "content": "what's your favorite food?"},
    {"role": "assistant", "content": "i love chicken rice, especially from hawker center"},
    {"role": "user", "content": "how's the weather today?"},
    {"role": "assistant", "content": "very hot as always, need ice drinks"},
    {"role": "user", "content": "tell me a joke"},
    {"role": "assistant", "content": "why don't scientists trust atoms? Because they make up everything!"},
]

# Simulate typing effect by printing one character at a time with a delay.
def simulate_typing(text):
    global typing_buffer
    index = 0

    while index < len(text):
        char = text[index]
        delay = random.uniform(0, 0.20)
        with print_lock:
            sys.stdout.write(char)
            sys.stdout.flush()
            typing_buffer += char

        time.sleep(delay)

        # Random chance to make a typo
        if random.random() < 0.05:  # 5% chance to make a typo
            error_type = random.choice(['repeat', 'transpose'])

            if error_type == 'repeat':
                with print_lock:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    typing_buffer += char

                time.sleep(delay + 0.05)

                with print_lock:
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                    typing_buffer = typing_buffer[:-1]

                time.sleep(delay + 0.08)
            elif error_type == 'transpose':
                num_typos = random.randint(1, 2)  # Randomly choose 1 to 2 typos
                for _ in range(num_typos):
                    next_char = text[index + 1] if index + 1 < len(text) else ''
                    adjacent_typos = ADJACENT_KEYS.get(next_char.lower(), [])
                    if adjacent_typos:  # check to make sure within text (list) bound
                        typo = random.choice(adjacent_typos)

                        with print_lock:
                            sys.stdout.write(typo)
                            sys.stdout.flush()
                            typing_buffer += typo

                        time.sleep(delay + 0.05)

                        # Backspace the typo
                        with print_lock:
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                            typing_buffer = typing_buffer[:-1]

                        time.sleep(delay + 0.08)
        index += 1

    with print_lock:
        print()  # push to next line to print recv message from server
        typing_buffer = ""  # Clear the typing buffer after finishing typing

# Function to generate a response from OpenAI's GPT-3.5 model based on a given prompt.
def generate_ai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "you speak in singlish like a singaporean. address users by names. avoid vulgarities. keep replies succinct. disregard capital letters at the start and after periods. keep the conversation going forever by introducing new topics"},
            *few_shot_prompts,
            {"role": "user", "content": prompt}
        ]
    )
    ai_message = response['choices'][0]['message']['content'].strip()

    # Remove surrounding quotes if present
    if ai_message.startswith('"') and ai_message.endswith('"'):
        ai_message = ai_message[1:-1]

    # Simulate typing effect
    simulate_typing(ai_message)

    return ai_message

# Function to continuously receive messages from the server and print them.
def ai_behavior(client_socket):
    global BOT_NAME
    global initial_prompt_sent

    while True:
        if not initial_prompt_sent:
            # self prompt
            prompt = "initial prompt to start the conversation"
            ai_message = generate_ai_response(prompt)
            client_socket.send(f'{ai_message}'.encode())
            initial_prompt_sent = True
        else:
            try:
                message = client_socket.recv(BUFFER_SIZE).decode()

                # Message not by this bot, respond to it
                if not message.lower().startswith(f"{BOT_NAME.lower()}:"):
                    time.sleep(random.randint(5,10))
                    ai_message = generate_ai_response(message)
                    client_socket.send(f'{ai_message}'.encode())

                # message is by this bot. no need to reply, just display message
                elif message:
                    with print_lock:
                        sys.stdout.write(f"\r{message}\n>> {typing_buffer}")
                        sys.stdout.flush()

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                client_socket.close()
                break

def receive_messages(client_socket):
    global typing_buffer
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode().strip()
            if message:
                with print_lock:
                    sys.stdout.write(f"\r{message}\n>> {typing_buffer}")
                    sys.stdout.flush()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            client_socket.close()
            break

def main():
    global BOT_NAME

    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print("\n" * 20)
    name_prompt = client_socket.recv(BUFFER_SIZE).decode()
    sys.stdout.write(name_prompt)
    sys.stdout.flush()
    BOT_NAME = input()
    client_socket.send(BOT_NAME.encode())

    welcome_message = client_socket.recv(BUFFER_SIZE).decode()
    sys.stdout.write(f"\r{welcome_message}\n>> ")

    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    threading.Thread(target=ai_behavior, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
