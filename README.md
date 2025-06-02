# iOS Animated Wallpaper Creator

This Python script provides a robust solution for converting standard MP4 video files into custom animated wallpapers for iOS devices, packaged in the `.tendies` format. This format is compatible with internal Apple tools like Mica and can be used on jailbroken or sideloaded devices.

## Features

* **MP4 to Image Sequence Conversion**: Efficiently extracts frames from your MP4 video and saves them as a sequence of JPEG images.
* **Core Animation (`.caml`) Generation**: Automatically creates the necessary `main.caml` files for both the background and floating layers. The script specifically utilizes a `CAKeyframeAnimation` structure to explicitly list each image frame, ensuring broad compatibility with iOS wallpaper systems.
* **iOS Bundle Structuring**: Generates all required `.plist` and other descriptor files, organizing them into the specific directory structure expected by iOS for `.tendies` wallpaper bundles.
* **Customization**: Allows you to define custom wallpaper names, target resolutions, and scaling factors to match various iPhone models.
* **Temporary File Management**: Uses temporary directories for intermediate files, ensuring a clean and automated process.

##  Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python 3.x**
* **OpenCV (`opencv-python`)**: Essential for video frame extraction and resizing.
* **FFmpeg**: While the script uses `cv2.VideoCapture` for frame extraction, FFmpeg is a fundamental tool for video processing and is generally recommended to have installed on your system.

You can install the required Python libraries using `pip`:

```bash
pip install opencv-python
