import socket
from stoppable_thread import StoppableThread
from handlers import handle_client


HOST = '0.0.0.0'
PORT = 8000


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    threads = []
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        try:
            client_socket, address = server_socket.accept()
            client_socket.settimeout(1.0)
            client_thread = StoppableThread(
                target=handle_client, args=(client_socket, address))
            client_thread.start()
            threads.append(client_thread)

        except KeyboardInterrupt:
            print('Exiting...')
            break

    print("Closing server socket.")
    server_socket.close()

    for thread in threads:
        thread.stop()
        thread.join()

    print("Server closed.")


if __name__ == '__main__':
    main()
