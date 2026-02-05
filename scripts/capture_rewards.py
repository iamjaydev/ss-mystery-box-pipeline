import subprocess
import sys
import time
import io
import csv
import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
import pytesseract


REPO_ROOT = Path(__file__).resolve().parents[1]
COORDS_FILE = REPO_ROOT / "state/tap_coords.txt"
CROP_BOX_FILE = REPO_ROOT / "state/crop_box.txt"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_FILE = REPO_ROOT / f"data/rewards_{timestamp}.csv"

DEBUG = False
DEBUG_DIR = "debug_screenshots"


REPO_ROOT.joinpath("state").mkdir(exist_ok=True)
REPO_ROOT.joinpath("data").mkdir(exist_ok=True)


def get_adb_devices():
    try:
        result = subprocess.run(
            ["adb", "devices"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        devices = []
        for line in result.stdout.splitlines():
            if "\tdevice" in line:
                devices.append(line.split("\t")[0])
        return devices
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run adb devices: {e.stderr.strip()}")


def print_instructions():
    print("""
================= CAPTURE SETUP =================

On your device:
- Go to the Mystery Box shop screen
- Scroll the shop ALL THE WAY TO THE TOP
- Do NOT scroll again after this

Workflow:
1. Choose option 1
   - Tap the Buy button ONCE on your phone
   - Tap once more to confirm you are back on the shop screen

2. Choose option 2
   - Enter the number of Mystery Boxes to open
   - Do NOT touch the device while the script runs

=================================================
""")


def select_device(serial=None):
    devices = get_adb_devices()
    if not devices:
        raise RuntimeError(
            "No ADB devices detected. Connect a device and try again.")

    if serial:
        if serial not in devices:
            raise RuntimeError(
                f"Device '{serial}' not found. Connected: {devices}")
        return serial

    if len(devices) > 1:
        raise RuntimeError(
            f"Multiple devices found: {devices}. Pass a serial as an argument.")

    return devices[0]


def capture_screenshot(device_serial):
    try:
        result = subprocess.run(
            ["adb", "-s", device_serial, "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return Image.open(io.BytesIO(result.stdout))
    except (subprocess.CalledProcessError, UnidentifiedImageError) as e:
        print(f"Error capturing screenshot: {e}")
        return None


def adb_tap(device_serial, x, y):
    subprocess.run(["adb", "-s", device_serial, "shell",
                   "input", "tap", str(x), str(y)])


def record_tap(device_serial):
    line_x = line_y = None
    # Note: getevent -lt produces hex values
    p = subprocess.Popen(
        ["adb", "-s", device_serial, "shell", "getevent", "-lt"],
        stdout=subprocess.PIPE,
        text=True
    )
    print(f"Waiting for a tap on device {device_serial}...")
    try:
        for line in p.stdout:
            if "ABS_MT_POSITION_X" in line:
                line_x = int(line.strip().split()[-1], 16)
            if "ABS_MT_POSITION_Y" in line:
                line_y = int(line.strip().split()[-1], 16)
            if line_x is not None and line_y is not None:
                with open(COORDS_FILE, "w") as f:
                    f.write(f"{line_x},{line_y}")
                print(f"Tap recorded: {line_x},{line_y}")
                break
    finally:
        p.terminate()
    time.sleep(0.5)


def open_boxes_and_capture_rewards(device_serial, crop_box):
    try:
        with open(COORDS_FILE) as f:
            x, y = f.read().strip().split(",")
    except FileNotFoundError:
        print("No tap recorded yet. Please choose option 1 first.")
        return

    n_str = input("Enter number of boxes to open: ")
    if not n_str.isdigit():
        return
    n = int(n_str)

    TIMELINE = {"buy": 0, "open": 1, "skip": 2, "capture": 3, "close": 4}

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["reward"])

    for i in range(n):
        start_time = time.time()
        print(f"Processing box {i + 1}/{n}...")

        for action, delay in TIMELINE.items():
            wait = max(0, delay - (time.time() - start_time))
            time.sleep(wait)

            if action == "capture":
                screenshot = capture_screenshot(device_serial)
                if screenshot:
                    cropped = ImageOps.autocontrast(
                        ImageOps.grayscale(screenshot.crop(crop_box)))
                    text = pytesseract.image_to_string(cropped).strip()
                    print(f" > Found: {text}")
                    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f_csv:
                        csv.writer(f_csv).writerow([text])
            else:
                adb_tap(device_serial, x, y)

    print(f"\nDone. Results saved to {CSV_FILE}")


def main():
    serial_arg = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        device_serial = select_device(serial_arg)
        print(f"Active Device: {device_serial}")
        print_instructions()

        if not CROP_BOX_FILE.exists():
            print(
                f"Error: {CROP_BOX_FILE} missing. Run crop selection script first.")
            sys.exit(1)

        with open(CROP_BOX_FILE) as f:
            crop_box = tuple(map(int, f.read().strip().split(",")))

        while True:
            print("\n--- BOX OPENER BOT ---")
            print("1. Record Buy Button Tap")
            print("2. Open Mystery Boxes")
            print("3. Exit")

            choice = input("Choice: ")

            if choice == "1":
                record_tap(device_serial)
            elif choice == "2":
                open_boxes_and_capture_rewards(device_serial, crop_box)
            elif choice == "3":
                break
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
