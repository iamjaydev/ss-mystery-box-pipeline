# ss-mystery-box-pipeline

Automated pipeline for opening **Subway Surfers Mystery Boxes**, extracting rewards from an Android device, and analyzing results.

## Features

- Auto-opens Mystery Boxes via ADB
- Captures reward screenshots
- Extracts reward text with OCR
- Saves rewards to CSV
- Cleans and normalizes data
- Analyzes distributions and returns
- Visualizes probabilities and outcomes

## Prerequisites

- **Python 3.9+**
- **ADB (Android Platform Tools)**
  Required for device control and screen capture
  Download: https://developer.android.com/tools/releases/platform-tools

  Verify:

  ```
  adb version
  ```

- **Tesseract OCR**
  Required for reward text extraction
  Install using the official instructions:
  [https://github.com/tesseract-ocr/tesseract#installing-tesseract](https://github.com/tesseract-ocr/tesseract#installing-tesseract)

  Verify:

  ```
  tesseract --version
  ```

- **Android device**
  - USB debugging enabled

## Installation

1. **Clone the repository**

   ```
   git clone https://github.com/iamjaydev/ss-mystery-box-pipeline.git
   cd ss-mystery-box-pipeline
   ```

2. **Install Python dependencies**

   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Connect device via ADB**
   - Connect the device and verify it is detected:

     ```
     adb devices
     ```

   - Reference: [https://developer.android.com/tools/adb](https://developer.android.com/tools/adb)

2. **Select the reward text crop region**
   - Run the crop selection script:

     ```
     python scripts/select_crop_box.py
     ```

   - Select the area where the reward text appears
   - The crop region is saved for future runs

3. **Capture Mystery Box rewards**
   - Run the capture script:

     ```
     python scripts/capture_rewards.py
     ```

   - The script will:
     - Open Mystery Boxes automatically
     - Capture reward screenshots
     - Extract reward text using OCR
     - Save results to CSV files in the `data/` directory

4. **Analyze and visualize results**
   - Run the visualization script:

     ```
     python scripts/visualize_results.py
     ```

   - Generates summary statistics and plots for reward distribution and returns

Ensure the game UI remains unchanged during capture to avoid OCR or tap errors.

Here is the corrected version with **“Enable Developer Options…” moved from Installation to Usage**, without changing tone or detail level.

---

## Installation

1. **Clone the repository**

   ```
   git clone https://github.com/iamjaydev/ss-mystery-box-pipeline.git
   cd ss-mystery-box-pipeline
   ```

2. **Install Python dependencies**

   ```
   pip install -r requirements.txt
   ```

---

## Usage

1. **Enable Developer Options on your Android device**
   - Enable **USB debugging**
   - Connect the device via USB
   - Confirm connection:

     ```
     adb devices
     ```

   - Reference: [https://developer.android.com/tools/adb](https://developer.android.com/tools/adb)

2. **Prepare the game**
   - Launch Subway Surfers
   - Navigate to the Mystery Box screen
   - Open one Mystery Box
   - When the reward appears, proceed to the next step

3. **Select the OCR crop region**
   - On your computer, from the project root directory, run:

     ```
     python scripts/select_crop_box.py
     ```

   - When the screenshot opens, select the region containing the reward text
   - The selected crop region is saved for future runs

4. **Capture Mystery Box rewards**
   - Run the script from the project root and follow the on-screen instructions:

     ```
     python scripts/capture_rewards.py
     ```

5. **Analyze and visualize results**

   ```
   python scripts/visualize_results.py
   ```

   - Generates summary statistics and plots

## Limitations

- OCR may be inaccurate; the cleaning script assumes consistent errors and may need adjustments
- Timing-sensitive: delays, pop-ups, or slow device responses can disrupt automation
