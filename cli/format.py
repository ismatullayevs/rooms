import curses
import json

def render(stdscr, messages, room_name, nickname, socket, stop_event):
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.timeout(10)
    
    stdscr.addstr(0, 0, "")
    
    scroll_pos = 0
    
    input_buffer = ''
    
    while not stop_event.is_set():
        height, width = stdscr.getmaxyx()
        
        display_height = height - 2
        
        stdscr.clear()
        stdscr.addstr(0, 0, f"Hi {nickname}, welcome to {room_name}")
        for idx, message in enumerate(messages[scroll_pos:scroll_pos + display_height]):
            stdscr.addstr(idx + 1, 0, f"{message}")

        stdscr.addstr(height - 1, 0, "Message: " + input_buffer)
        stdscr.clrtoeol()
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            if scroll_pos > 0:
                scroll_pos -= 1

        elif key == curses.KEY_DOWN:
            if scroll_pos < max(0, len(messages) - display_height):
                scroll_pos += 1

        elif key == curses.KEY_BACKSPACE or key == 127:
            input_buffer = input_buffer[:-1]

        elif key == ord('\n'):
            user_input = input_buffer.strip()
            if user_input.lower() == 'q':
                break
            
            if user_input:
                socket.send(json.dumps({
                    'type': 'message',
                    'room': room_name,
                    'nickname': nickname,
                    'message': user_input,
                }).encode())
                
            input_buffer = ''
            
            if len(messages) > display_height:
                scroll_pos = len(messages) - display_height

        elif key == -1:
            pass

        elif key < 256:
            input_buffer += chr(key)
        
    stdscr.clear()
    stdscr.addstr(0, 0, "Goodbye!")
    stdscr.refresh()
    stdscr.getch()
