import sys
import struct
import json

# Helper to read a message from Chrome
def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack('<I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

# Helper to send a message to Chrome
def send_message(message):
    encoded = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('<I', len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()

if __name__ == '__main__':
    while True:
        msg = read_message()
        # Example: just echo back
        if msg.get('type') == 'fill_plate':
            # Here you would trigger the plate fill logic
            send_message({'status': 'received', 'plate': msg.get('plate')})
        else:
            send_message({'status': 'unknown_command'})
