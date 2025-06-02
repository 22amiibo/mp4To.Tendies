import cv2
import os
import ffmpeg
import uuid
import plistlib
from shutil import rmtree, make_archive
from tempfile import mkdtemp
from datetime import datetime

def create_tendies_from_mp4(input_mp4_path, wallpaper_name="CustomWallpaper", 
                            target_resolution_width=1290, target_resolution_height=2796, scale_factor=3,
                            identifier=9136): # Added identifier for Wallpaper.plist
    """
    Converts an MP4 video into an iOS .tendies animated wallpaper file with specified structure and naming.

    Args:
        input_mp4_path (str): The path to the input MP4 video file.
        wallpaper_name (str): The base name for the wallpaper (e.g., "MyAwesomeScene").
        target_resolution_width (int): Target width for the wallpaper (e.g., 1290 for iPhone 15 Pro Max).
        target_resolution_height (int): Target height for the wallpaper (e.g., 2796 for iPhone 15 Pro Max).
        scale_factor (int): The @Nx scale factor (e.g., 3 for @3x).
        identifier (int): An integer identifier for the wallpaper variant, used in Wallpaper.plist.
    """
    if not os.path.exists(input_mp4_path):
        print(f"Error: Input MP4 file not found at {input_mp4_path}")
        return

    # --- Derived Naming and Resolution ---
    resolution_str = f"{target_resolution_width}w-{target_resolution_height}h@{scale_factor}x~iphone"
    wallpaper_folder_name = f"{wallpaper_name}-{resolution_str}.wallpaper"
    background_ca_name = f"{wallpaper_name}_Background-{resolution_str}.ca"
    floating_ca_name = f"{wallpaper_name}_Floating-{resolution_str}.ca"

    # --- Temporary Directory Setup ---
    temp_dir = mkdtemp(prefix="tendies_temp_")
    print(f"Working in temporary directory: {temp_dir}")

    try:
        # Define UUIDs and base paths
        wallpaper_uuid = str(uuid.uuid4()).upper()
        provider_descriptor_uuid = str(uuid.uuid4()).upper() # Unique for provider descriptor

        descriptors_path = os.path.join(temp_dir, "descriptors")
        uuid_base_path = os.path.join(descriptors_path, wallpaper_uuid)
        versions_path = os.path.join(uuid_base_path, "versions", "1")
        contents_path = os.path.join(versions_path, "contents")
        
        wallpaper_bundle_path = os.path.join(contents_path, wallpaper_folder_name)
        background_ca_bundle_path = os.path.join(wallpaper_bundle_path, background_ca_name)
        floating_ca_bundle_path = os.path.join(wallpaper_bundle_path, floating_ca_name)

        # Create main directory structure
        os.makedirs(background_ca_bundle_path, exist_ok=True)
        os.makedirs(floating_ca_bundle_path, exist_ok=True)

        # --- Video Frame Extraction and assets generation ---
        cap = cv2.VideoCapture(input_mp4_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {input_mp4_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps

        background_assets_path = os.path.join(background_ca_bundle_path, "assets")
        floating_assets_path = os.path.join(floating_ca_bundle_path, "assets")
        os.makedirs(background_assets_path, exist_ok=True)
        os.makedirs(floating_assets_path, exist_ok=True)

        print(f"Extracting {frame_count} frames at {fps} FPS...")
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Resize frame to target resolution before saving
            resized_frame = cv2.resize(frame, (target_resolution_width, target_resolution_height))
            frame_filename = os.path.join(background_assets_path, f"{frame_idx:05d}.jpg")
            cv2.imwrite(frame_filename, resized_frame)
            frame_idx += 1
        cap.release()
        print(f"Extracted {frame_idx} frames.")

        # --- Generate main.caml for background and floating layers ---
        # This CAML defines a sequence of images.
        # It's a simplified version of what Mica generates, focusing on image sequence playback.
        # Note: The PatrickSeahorse.zip main.caml defines state-based scaling for a static image.
        # For an MP4, we stick to the image sequence animation.
        main_caml_template = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>view</key>
    <dict>
        <key>backgroundColor</key>
        <string>0 0 0 0</string> <key>drawsAsynchronously</key>
        <false/>
        <key>sublayers</key>
        <array>
            <dict>
                <key>bounds</key>
                <string>{{0, 0}, {%d, %d}}</string>
                <key>contents</key>
                <dict>
                    <key>initialImage</key>
                    <string>assets/00000.jpg</string>
                    <key>frameDuration</key>
                    <real>%.6f</real>
                    <key>frameCount</key>
                    <integer>%d</integer>
                    <key>imageFormat</key>
                    <string>jpg</string>
                    <key>imageNamePattern</key>
                    <string>assets/%%05d.jpg</string>
                    <key>loop</key>
                    <true/>
                    <key>type</key>
                    <string>ImageSequence</string>
                </dict>
                <key>name</key>
                <string>ContentLayer</string>
                <key>position</key>
                <string>{{0, 0}}</string>
                <key>type</key>
                <string>CALayer</string>
            </dict>
        </array>
    </dict>
</dict>
</plist>
"""
        # Format CAML with video dimensions and frame details
        formatted_main_caml = main_caml_template % (target_resolution_width, target_resolution_height, 1.0/fps, frame_count)

        with open(os.path.join(background_ca_bundle_path, "main.caml"), "w") as f:
            f.write(formatted_main_caml)
        
        # For floating.ca, we'll use a minimal CAML if no distinct floating content.
        # If there were separate floating elements, this would be different.
        minimal_main_caml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>view</key>
    <dict>
        <key>backgroundColor</key>
        <string>0 0 0 0</string>
        <key>drawsAsynchronously</key>
        <false/>
        <key>sublayers</key>
        <array/>
    </dict>
</dict>
</plist>
"""
        with open(os.path.join(floating_ca_bundle_path, "main.caml"), "w") as f:
            f.write(minimal_main_caml)

        # --- Generate index.xml for background and floating layers ---
        index_xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>assetManifest</key>
	<string>assetManifest.caml</string>
	<key>documentHeight</key>
	<real>{target_resolution_height}</real>
	<key>documentResizesToView</key>
	<true/>
	<key>documentWidth</key>
	<real>{target_resolution_width}</real>
	<key>dynamicGuidesEnabled</key>
	<true/>
	<key>geometryFlipped</key>
	<false/>
	<key>guidesEnabled</key>
	<true/>
	<key>interactiveMouseEventsEnabled</key>
	<true/>
	<key>interactiveShowsCursor</key>
	<true/>
	<key>interactiveTouchEventsEnabled</key>
	<false/>
	<key>loopEnd</key>
	<real>{duration}</real>
	<key>loopStart</key>
	<real>0.0</real>
	<key>loopingEnabled</key>
	<true/>
	<key>multitouchDisablesMouse</key>
	<false/>
	<key>multitouchEnabled</key>
	<false/>
</dict>
</plist>
"""
        with open(os.path.join(background_ca_bundle_path, "index.xml"), "w") as f:
            f.write(index_xml_content)
        with open(os.path.join(floating_ca_bundle_path, "index.xml"), "w") as f:
            f.write(index_xml_content)

        # --- Generate assetManifest.caml (minimal valid XML) ---
        # As no specific content was provided or found, an empty dictionary plist.
        asset_manifest_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict/>
</plist>
"""
        with open(os.path.join(background_ca_bundle_path, "assetManifest.caml"), "w") as f:
            f.write(asset_manifest_content)
        with open(os.path.join(floating_ca_bundle_path, "assetManifest.caml"), "w") as f:
            f.write(asset_manifest_content)

        # --- Generate Wallpaper.plist (Updated based on PatrickSeahorse.zip) ---
        wallpaper_plist_content = {
            "appearanceAware": 1,
            "assets": {
                "lockAndHome": {
                    "default": {
                        "backgroundAnimationFileName": background_ca_name,
                        "floatingAnimationFileNameKey": floating_ca_name,
                        "identifier": identifier,
                        "name": wallpaper_name,
                        "type": "LayeredAnimation"
                    }
                }
            },
            "contentVersion": 2.01,
            "family": wallpaper_name,
            "identifier": identifier,
            "logicalScreenClass": resolution_str,
            "name": wallpaper_name,
            "preferredProminentColor": { # Example colors, can be dynamically determined if needed
                "dark": "#4C9CBC",
                "default": "#4CA4BC"
            },
            "version": 1
        }
        with open(os.path.join(wallpaper_bundle_path, "Wallpaper.plist"), "wb") as f:
            plistlib.dump(wallpaper_plist_content, f)

        # --- Generate providerInfo.plist (Updated based on PatrickSeahorse.zip) ---
        provider_info_plist_content = {
            "kConfigurationLastUseDateKey": datetime.now() # Current date/time
        }
        with open(os.path.join(uuid_base_path, "providerInfo.plist"), "wb") as f:
            plistlib.dump(provider_info_plist_content, f, fmt=plistlib.FMT_XML) # Ensure XML format

        # --- Generate com.apple.posterkit.role.identifier ---
        with open(os.path.join(uuid_base_path, "com.apple.posterkit.role.identifier"), "w") as f:
            f.write("PRPosterRoleLockScreen")

        # --- Generate com.apple.posterkit.provider.descriptor.identifier ---
        with open(os.path.join(uuid_base_path, "com.apple.posterkit.provider.descriptor.identifier"), "w") as f:
            f.write(provider_descriptor_uuid) # Use the unique identifier generated earlier

        # --- Generate com.apple.posterkit.provider.contents.userInfo ---
        # Content provided by the user. The 'data' field 'e30=' is base64 for empty dict {}.
        user_info_plist_content = {
            "posterEnvironmentOverrides": b"e30=",
            "wallpaperRepresentingFileName": wallpaper_folder_name,
            "wallpaperRepresentingIdentifier": str(identifier) # Needs to be string if PatrickSeahorse was string
        }
        with open(os.path.join(uuid_base_path, "com.apple.posterkit.provider.contents.userInfo"), "wb") as f:
            plistlib.dump(user_info_plist_content, f)


        print("All files created.")

        # --- Zip the descriptors folder and rename to .tendies ---
        # The output .tendies file will be created in the current working directory
        output_tendies_file = f"{wallpaper_name}.tendies" # Define output name here for consistency
        output_base_name = os.path.splitext(output_tendies_file)[0]
        
        # make_archive creates a zip in the current working directory from the specified source
        # The root_dir here should be 'temp_dir' and base_dir should be 'descriptors'
        output_zip_path = make_archive(output_base_name, 'zip', root_dir=temp_dir, base_dir="descriptors")
        os.rename(output_zip_path, output_tendies_file)

        print(f"Successfully created .tendies file: {output_tendies_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if os.path.exists(temp_dir):
            rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")

# --- How to use the script ---
if __name__ == "__main__":
    # Example usage:
    # Ensure you have 'input.mp4' in the same directory, or provide a full path.
    # You might need to install: pip install opencv-python ffmpeg-python
    
    # Create a dummy input.mp4 for testing if you don't have one:
    # ffmpeg -f lavfi -i "testsrc=duration=5:size=1280x720:rate=30" -vf "format=yuv420p" input.mp4

    input_file = "input.mp4" # Replace with your MP4 file path
    
    # For iPhone 15 Pro Max (example):
    target_width = 1290
    target_height = 2796
    scale = 3

    create_tendies_from_mp4(input_file, 
                           wallpaper_name="MyAnimatedWallpaper", 
                           target_resolution_width=target_width, 
                           target_resolution_height=target_height, 
                           scale_factor=scale,
                           identifier=9136) # Example identifier, adjust as needed

    create_tendies_from_mp4("jakecopy.mp4", wallpaper_name="JakeCopy")