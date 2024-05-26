Terminal based chat app.

Run the server:
```bash
python server/main.py
```

Crate .env file with HOST and PORT of your server:
```.env
HOST="0.0.0.0"
PORT=8000
```

Run `create` to create a room:
```bash
python cli/main.py create friends
```

Run `join` to join a room:
```bash
python cli/main.py join friends
```