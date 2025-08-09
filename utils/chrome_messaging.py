import subprocess
import sys
import json
import os
from typing import Optional, Dict, Any

def send_plate_to_chrome(plate: str, host_script: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Send a license plate string to the Chrome extension via native messaging host.
    host_script: Path to native_host.py (default: ./native_host.py)
    """
    if host_script is None:
        host_script = os.path.join(os.path.dirname(__file__), '..', 'native_host.py')
    host_script = os.path.abspath(host_script)
    message = {"type": "fill_plate", "plate": plate}
    # Prepare the message in native messaging format
    encoded = json.dumps(message).encode('utf-8')
    length = len(encoded)
    packed = length.to_bytes(4, byteorder='little') + encoded
    # Launch the native host as a subprocess
    try:
        proc = subprocess.Popen([
            sys.executable, host_script
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Ensure stdin and stdout are available
        if proc.stdin is None or proc.stdout is None:
            return {"error": "Failed to create subprocess pipes"}
            
        proc.stdin.write(packed)
        proc.stdin.flush()
        # Read response
        raw_length = proc.stdout.read(4)
        if len(raw_length) == 0:
            return None
        resp_length = int.from_bytes(raw_length, byteorder='little')
        resp = proc.stdout.read(resp_length)
        return json.loads(resp.decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}
