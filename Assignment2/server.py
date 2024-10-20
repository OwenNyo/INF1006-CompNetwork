import socket
import threading

# Constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 2048

# List to keep track of connected clients
clients = []
clients_lock = threading.Lock()

def handle_client(client_socket):
    global clients

    try:
        client_socket.send("Enter your name: ".encode())
        name = client_socket.recv(BUFFER_SIZE).decode().strip()

        # Send welcome message to the client
        server_message = f"[*] {name} has joined the chatroom!"
        welcome_message = f"Welcome {name} to the chatroom!"
        print(server_message)
        client_socket.send(welcome_message.encode())

        # Broadcast the joining message to all clients
        join_message = f"{name} has joined the chatroom!"
        broadcast(join_message)

        # Add the client to the list of clients
        with clients_lock:
            clients.append({
                'socket': client_socket,
                'name': name
            })

        # Handle client messages
        while True:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if message:
                # Format and print the message received from the client
                server_message = f"[*] {name}: {message}"
                formatted_message = f"{name}: {message}"
                print(server_message)

                # Broadcast the message to all clients
                broadcast(formatted_message)
            else:
                break
    except Exception as e:
        print(f"[*] Exception occurred for client {name}: {str(e)}")

    finally:
        # Client has left the chatroom
        leave_message = f"[*] {name} has left the chatroom!"
        print(leave_message)

        # Broadcast the leave message to all clients
        broadcast(leave_message)

        # Remove client from the list of clients
        with clients_lock:
            clients = [client for client in clients if client['socket'] != client_socket]

        # Close the client socket
        client_socket.close()

def broadcast(message):
    with clients_lock:
        for client in clients:
            try:
                client['socket'].send(message.encode())
            except Exception as e:
                # If sending fails, remove the client from the list
                print(f"[*] Error broadcasting to client: {str(e)}")
                clients.remove(client)

def main():
    # Initialize the server, accept clients, and handle them in separate threads
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)  # Change number of simultaneous clients as needed

    print(f'[*] Server is listening on {SERVER_IP}:{SERVER_PORT}')

    while True:
        client_socket, client_address = server.accept()
        print(f"[*] New connection: {client_address} has joined the chatroom.")

        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == '__main__':
    main()
