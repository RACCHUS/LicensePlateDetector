
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.chrome_messaging import send_plate_to_chrome

if __name__ == "__main__":
    # You can change this to any test plate string
    test_plate = "TEST1234"
    if len(sys.argv) > 1:
        test_plate = sys.argv[1]
    print(f"Sending test plate: {test_plate}")
    response = send_plate_to_chrome(test_plate)
    print(f"Native messaging response: {response}")
