Here’s a concise and clear **README** for your script, focusing on how to run it and what features it offers:

---

# 🎥 Create iOS `.tendies` Live Wallpapers from MP4

This Python script converts any MP4 video into a `.tendies` file — the format used by iOS for custom animated lock screen wallpapers (used with PosterKit). It's designed for advanced users who want full control over the live wallpaper format.

## ✅ Features

* **MP4 to .tendies conversion**: Transforms any MP4 into a valid iOS animated wallpaper.
* **Automatic frame extraction**: Grabs frames at the source video’s FPS and resizes them.
* **CAML generation**: Builds the required `main.caml`, `index.xml`, and `assetManifest.caml` files for layered animation.
* **Supports iPhone resolutions**: Defaults to 1290x2796 @3x for iPhone 15 Pro Max, but customizable.
* **Complete `.tendies` output**: Includes `Wallpaper.plist`, `providerInfo.plist`, and other required PosterKit identifiers.
* **Clean temporary files**: Uses a temp directory and cleans up after the archive is created.

## 🛠 Requirements

Install required packages:

```bash
pip install opencv-python ffmpeg-python
```

Make sure you have `ffmpeg` installed on your system.

## ▶️ How to Run

Save your video as `input.mp4` (or another name) and run the script:

```bash
python your_script_name.py
```

The script will:

1. Extract all frames from the MP4.
2. Resize them to the iPhone’s wallpaper resolution.
3. Generate all required `.plist`, `.caml`, and `.xml` files.
4. Zip the structure and rename it to a `.tendies` file.

The resulting file will be:

```
MyAnimatedWallpaper.tendies
```

You can change output settings directly in the `create_tendies_from_mp4()` function:

```python
create_tendies_from_mp4(
    input_mp4_path="your_video.mp4",
    wallpaper_name="MyAnimatedWallpaper",
    target_resolution_width=1290,
    target_resolution_height=2796,
    scale_factor=3,
    identifier=9136
)
```

---
