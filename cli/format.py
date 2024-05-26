import curses
import json

def render(stdscr, messages, room_name, nickname, socket):
    stdscr.clear()
    
    # Instructions
    stdscr.addstr(0, 0, "")
    
    # Scroll position
    scroll_pos = 0
    
    # To hold the current input buffer
    input_buffer = ''
    
    # Main loop
    while True:
        # Get the screen height and width
        height, width = stdscr.getmaxyx()
        
        # Calculate the number of lines available for displaying to-dos
        display_height = height - 2  # 1 for instructions, 1 for the input prompt
        
        # Display the to-do list with scrolling
        stdscr.clear()
        stdscr.addstr(0, 0, f"Hi {nickname}, welcome to {room_name}")
        for idx, todo in enumerate(messages[scroll_pos:scroll_pos + display_height]):
            stdscr.addstr(idx + 1, 0, f"{idx + 1 + scroll_pos}. {todo}")

        # Display the prompt at the bottom
        stdscr.addstr(height - 1, 0, "Message: " + input_buffer)
        stdscr.clrtoeol()  # Clear to the end of the line to handle shorter inputs after longer ones
        
        # Refresh the screen
        stdscr.refresh()
        
        # Get user input
        key = stdscr.getch()
        
        if key == curses.KEY_UP:
            # Scroll up
            if scroll_pos > 0:
                scroll_pos -= 1
        elif key == curses.KEY_DOWN:
            # Scroll down
            if scroll_pos < max(0, len(messages) - display_height):
                scroll_pos += 1
        elif key == curses.KEY_BACKSPACE or key == 127:
            # Handle backspace
            input_buffer = input_buffer[:-1]
        elif key == ord('\n'):
            # Handle text input
            user_input = input_buffer.strip()
            if user_input.lower() == 'q':
                break
            
            # Add the input to the to-do list
            if user_input:
                socket.send(json.dumps({
                    'type': 'message',
                    'room': room_name,
                    'nickname': nickname,
                    'message': user_input,
                }).encode())
                
            # Reset input buffer
            input_buffer = ''
            
            # Reset scroll position to show the latest item
            if len(messages) > display_height:
                scroll_pos = len(messages) - display_height
        elif key < 256:
            # Append character to input buffer
            input_buffer += chr(key)
        
    # Cleanup
    stdscr.clear()
    stdscr.addstr(0, 0, "Goodbye!")
    stdscr.refresh()
    stdscr.getch()
