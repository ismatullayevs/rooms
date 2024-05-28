import socket
import threading
import json
import re


rooms = {}


def broadcast(room_name, data, exclude=None):
    exclude = exclude or []
    if room_name not in rooms:
        return

    for nickname, client_socket in rooms[room_name]:
        if client_socket in exclude:
            continue

        try:
            client_socket.send(data)
        except Exception as e:
            print(e)
            client_socket.close()
            remove_client(room_name, nickname, client_socket)


def remove_client(room_name, nickname, client_socket):
    if room_name not in rooms:
        return

    if (nickname, client_socket) not in rooms[room_name]:
        return

    rooms[room_name].remove((nickname, client_socket))
    print(f"User '{nickname}' left room '{room_name}'.")
    broadcast(room_name, json.dumps({
        'type': 'server_message',
        'message': f"'{nickname}' left room '{room_name}'.",
    }).encode())

    if not rooms[room_name]:
        del rooms[room_name]
        print(f"Room '{room_name}' deleted (no users).")


def handle_client(client_socket, address):
    print(f"New connection from {address}")
    nickname, roomname = None, None

    while not threading.current_thread().stopped():
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            data = json.loads(data.decode())
            print(data)

            if data['type'] == 'join':
                if data['room'] not in rooms:
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'room_not_found',
                        'message': f"Room '{data['room']}' does not exist.",
                    }).encode())
                    break

                if not re.match(r'^[a-zA-Z0-9_]+$', data['nickname']):
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'invalid_nickname',
                        'message': "Nickname can only contain letters, numbers, and underscores.",
                    }).encode())
                    continue

                if data['nickname'] in [user[0] for user in rooms[data['room']]]:
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'nickname_taken',
                        'message': f"Nickname '{data['nickname']}' is already taken.",
                    }).encode())
                    continue

                if client_socket in rooms[data['room']]:
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'already_in_room',
                        'message': f"You are already in room '{data['room']}'.",
                    }).encode())
                    break

                nickname, roomname = data['nickname'], data['room']
                rooms[data['room']].append((data['nickname'], client_socket))
                print(f"User '{data['nickname']}' joined room '{
                      data['room']}'.")
                print(rooms)
                broadcast(data['room'], json.dumps({
                    'type': 'server_message',
                    'message': f"'{data['nickname']}' joined room '{data['room']}'.",
                }).encode())

            elif data['type'] == 'create':
                if data['room'] in rooms:
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'room_exists',
                        'message': f"Room '{data['room']}' already exists.",
                    }).encode())
                    break

                if not re.match(r'^[a-zA-Z0-9_]+$', data['room']):
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'invalid_room_name',
                        'message': "Room name can only contain letters, numbers, and underscores.",
                    }).encode())
                    break

                if not re.match(r'^[a-zA-Z0-9_]+$', data['nickname']):
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'invalid_nickname',
                        'message': "Nickname can only contain letters, numbers, and underscores.",
                    }).encode())
                    continue

                rooms[data['room']] = []
                print(f"Room '{data['room']}' created.")
                client_socket.send(json.dumps({
                    'type': 'server_message',
                    'message': f"Room '{data['room']}' created.",
                }).encode())
                rooms[data['room']].append((data['nickname'], client_socket))
                print(f"User '{data['nickname']}' joined room '{
                      data['room']}'.")
                client_socket.send(json.dumps({
                    'type': 'server_message',
                    'message': f"'{data['nickname']}' joined room '{data['room']}'.",
                }).encode())
                nickname, roomname = data['nickname'], data['room']

            elif data['type'] == 'message':
                if data['room'] not in rooms:
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'room_not_found',
                        'message': f"Room '{data['room']}' does not exist.",
                    }).encode())
                    break

                if (data['nickname'], client_socket) not in rooms[data['room']]:
                    client_socket.send(json.dumps({
                        'type': 'error',
                        'code': 'not_in_room',
                        'message': f"You are not in room '{data['room']}'.",
                    }).encode())
                    break

                broadcast(data['room'], json.dumps({
                    'type': 'message',
                    'sender': data['nickname'],
                    'message': data['message'],
                }).encode())

        except socket.timeout:
            continue

        except Exception as e:
            print(e)
            break

    client_socket.close()
    if roomname:
        remove_client(roomname, nickname, client_socket)
    print(f"Connection closed from {address}")
