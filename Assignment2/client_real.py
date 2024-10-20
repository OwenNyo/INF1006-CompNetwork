import socket
import threading
import sys

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 2048

def receive_message(client_socket):
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if message.strip():
                sys.stdout.write(f"\r{message}\n>> ")
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def main():
    # Establish TCP connection with the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    # Receive the prompt to enter a name and send the name
    print("\n" * 20)
    name_prompt = client_socket.recv(BUFFER_SIZE).decode()
    sys.stdout.write(name_prompt)
    sys.stdout.flush()
    name = input()
    client_socket.send(name.encode())

    # Start a thread to continuously receive messages from the server
    threading.Thread(target=receive_message, args=(client_socket,)).start()

    # Main loop to send messages from client to server
    while True:
        message = input()
        if message.strip():
            client_socket.send(message.encode())


if __name__ == '__main__':
    main()
