import subprocess
import io
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from PIL import Image, UnidentifiedImageError
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = REPO_ROOT / "state/crop_box.txt"
crop_box = None

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
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to run adb devices: {e.stderr.strip()}")

    devices = []
    for line in result.stdout.splitlines():
        if "\tdevice" in line:
            devices.append(line.split("\t")[0])

    return devices


def select_device(serial=None):

    devices = get_adb_devices()

    if not devices:
        raise RuntimeError("No ADB devices detected.\n"
                           "Make sure an Android device or emulator is connected and ADB is working."
                           )

    if serial:
        if serial not in devices:
            raise RuntimeError(
                f"Specified device '{serial}' not found. Connected devices: {devices}"
            )
        return serial

    if len(devices) > 1:
        raise RuntimeError(
            f"Multiple devices connected: {devices}. "
            "Please specify a device serial as a command-line argument."
        )

    return devices[0]


def capture_screenshot(device_serial):
    try:
        result = subprocess.run(
            ["adb", "-s", device_serial, "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        if not result.stdout:
            raise RuntimeError("ADB returned empty screenshot data.")

        return Image.open(io.BytesIO(result.stdout))

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"ADB screencap failed: {e.stderr.decode(errors='ignore').strip()}"
        )

    except UnidentifiedImageError:
        raise RuntimeError("Failed to decode screenshot image.")


def onselect(eclick, erelease):
    global crop_box

    if eclick.xdata is None or erelease.xdata is None:
        return

    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)

    crop_box = (
        min(x1, x2),
        min(y1, y2),
        max(x1, x2),
        max(y1, y2),
    )

    print("Selected crop box:", crop_box)


def main(device_serial=None):
    global crop_box

    try:
        serial = select_device(device_serial)
        print(f"Using device: {serial}")

        image = capture_screenshot(serial)

        fig, ax = plt.subplots()
        ax.imshow(image)
        ax.set_title("Drag to select crop area. Close window when done.")

        rect_selector = RectangleSelector(
            ax,
            onselect,
            interactive=True,
            button=[1],
            minspanx=5,
            minspany=5,
            spancoords="pixels",
        )

        plt.show()

        if crop_box:
            with open(OUTPUT_FILE, "w") as f:
                f.write(",".join(map(str, crop_box)))
            print(f"Crop box saved to {OUTPUT_FILE}: {crop_box}")
        else:
            print("No crop box selected.")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    serial_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(serial_arg)
