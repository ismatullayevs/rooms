import os
import socket
import sys
import threading
from dotenv import load_dotenv
import json

load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

if not HOST or not PORT:
    print("Please provide HOST and PORT in .env file.")
    sys.exit(1)

PORT = int(PORT)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.settimeout(1.0)

stop_event = threading.Event()

def receive_messages():
    while not stop_event.is_set():
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            data = json.loads(data.decode())

            if data['type'] == 'error':
                print(f"Error: {data['message']}\r")

            if data['type'] == 'message':
                print(f"{data['sender']}: {data['message']}\r")

            if data['type'] == 'server_message':
                print(f"------- {data['message']} -------\r")

        except socket.timeout:
            continue

        except Exception as e:
            print(f"Exception in receive_messages: {e}")
            client_socket.close()
            break

    client_socket.close()
    print("Connection closed.")

def main():
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

    action = sys.argv[1]
    room_name = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else None
    if room_name is None:
        print("Please provide a room name.")
        sys.exit(1)

    nickname = input("Enter your nickname: ")

    client_socket.send(json.dumps({
        'type': action,
        'room': room_name,
        'nickname': nickname,
    }).encode())

    try:
        while True:
            message = input()
            print(message)
            if message.lower() == 'exit':
                break

            client_socket.send(json.dumps({
                'type': 'message',
                'room': room_name,
                'nickname': nickname,
                'message': message,
            }).encode())
    except KeyboardInterrupt:
        pass

    print("\nExiting...")
    stop_event.set()
    receive_thread.join()
    client_socket.close()

if __name__ == '__main__':
    main()
