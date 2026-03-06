#!/usr/bin/env python3
"""
Interactive wrapper for exif_editor.py
Prompts for each input field and builds the command
"""

import os
import subprocess
import sys
from pathlib import Path
from camera_presets import CAMERA_PRESETS



def ask_input(prompt: str, required: bool = False, default: str = None) -> str:
    """
    Ask user for input with optional default value.
    If required=True, keep asking until non-empty answer.
    """
    if default:
        display_prompt = f"{prompt} [{default}]: "
    else:
        display_prompt = f"{prompt}: "
    
    while True:
        response = input(display_prompt).strip()
        if response:
            return response
        if default:
            return default
        if not required:
            return ""
        print("  ⚠️  This field is required. Please enter a value.")


def ask_choice(prompt: str, choices: list, default: str = None) -> str:
    """
    Ask user to choose from a list of options.
    """
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " ← default" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    
    while True:
        response = input("Enter your choice (number or name): ").strip()
        
        # Check if it's a number
        if response.isdigit():
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
            print(f"  ⚠️  Please enter a number between 1 and {len(choices)}")
        # Check if it's a choice name
        elif response in choices:
            return response
        # Default if empty
        elif not response and default:
            return default
        else:
            print(f"  ⚠️  Invalid choice. Please select from: {', '.join(choices)}")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Ask yes/no question.
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if response in ("y", "yes"):
        return True
    if response in ("n", "no"):
        return False
    return default


def main():
    print("\n" + "="*70)
    print("  EXIF Editor — Interactive Mode")
    print("="*70 + "\n")
    
    # ============================================================================
    # 1. Input path (required)
    # ============================================================================
    print("📁 Input Configuration")
    print("-" * 70)
    input_path = ask_input("Path to image or folder", required=True)
    
    if not Path(input_path).exists():
        print(f"❌ Error: Path does not exist: {input_path}")
        sys.exit(1)
    
    is_batch = Path(input_path).is_dir()
    print(f"  → {'Batch mode (folder)' if is_batch else 'Single image'}")
    
    # ============================================================================
    # 2. Camera preset
    # ============================================================================
    print("\n📷 Camera Preset")
    print("-" * 70)
    presets = ["random"] + list(CAMERA_PRESETS.keys())
    preset = ask_choice("Which camera preset?", presets, default="random")
    print(f"  → {preset}")
    
    # ============================================================================
    # 3. Randomize exposure settings
    # ============================================================================
    print("\n⚙️  Exposure Settings")
    print("-" * 70)
    randomize = ask_yes_no("Randomize ISO, shutter speed, and aperture?", default=True)
    print(f"  → {'Yes (randomized within realistic ranges)' if randomize else 'No (use preset defaults)'}")
    
    # ============================================================================
    # 4. Timestamp
    # ============================================================================
    print("\n📅 Timestamp")
    print("-" * 70)
    use_random_date = ask_yes_no("Use random timestamp?", default=True)
    
    fixed_datetime = None
    days_back = 365
    
    if use_random_date:
        days_back_input = ask_input("How many days back to randomize from? (e.g., 365)", default="365")
        try:
            days_back = int(days_back_input)
            print(f"  → Random date within last {days_back} days")
        except ValueError:
            print("  → Invalid input, using default: 365 days")
            days_back = 365
    else:
        fixed_datetime = ask_input("Fixed timestamp (format: YYYY:MM:DD HH:MM:SS)", required=True)
        print(f"  → {fixed_datetime}")
    
    # ============================================================================
    # 5. Location / GPS
    # ============================================================================
    print("\n📍 Location / GPS")
    print("-" * 70)
    location_choice = ask_choice(
        "How to set location?",
        ["City name (geocoded)", "Manual GPS coordinates", "No GPS data"],
        default="City name (geocoded)"
    )
    
    city = None
    lat = None
    lon = None
    alt = None
    
    if location_choice == "City name (geocoded)":
        city = ask_input("City name (e.g., 'Mumbai', 'Paris', 'Tokyo')", required=True)
        print(f"  → Will geocode: {city}")
        if is_batch:
            print(f"  → Each image will have unique GPS ±500m around the city")
    elif location_choice == "Manual GPS coordinates":
        lat = ask_input("Latitude (e.g., 19.0760)", required=True)
        lon = ask_input("Longitude (e.g., 72.8777)", required=True)
        alt_input = ask_input("Altitude in meters (optional, press Enter to skip)")
        try:
            lat = float(lat)
            lon = float(lon)
            alt = float(alt_input) if alt_input else None
            print(f"  → GPS: {lat:.6f}°, {lon:.6f}°" + (f", {alt}m" if alt else ""))
        except ValueError:
            print("  ⚠️  Invalid GPS values, skipping location")
            lat = lon = alt = None
    else:
        print("  → No GPS data will be embedded")
    
    # ============================================================================
    # 6. Metadata fields
    # ============================================================================
    print("\n📝 Metadata")
    print("-" * 70)
    
    title = ask_input("Title / Image Description (optional)")
    description = ask_input("Description / Comment (optional)")
    artist = ask_input("Photographer / Artist name (optional)")
    copyright_str = ask_input("Copyright info (optional)")
    
    if title:
        print(f"  → Title: {title}")
    if description:
        print(f"  → Description: {description}")
    if artist:
        print(f"  → Artist: {artist}")
    if copyright_str:
        print(f"  → Copyright: {copyright_str}")
    
    # ============================================================================
    # 7. Output configuration
    # ============================================================================
    print("\n💾 Output")
    print("-" * 70)
    
    output_dir = None
    if is_batch:
        output_dir = ask_input(
            "Output folder for processed images",
            default="./output"
        )
        print(f"  → Output dir: {output_dir}")
    else:
        output_file = ask_input("Output file path (optional, leave empty to overwrite)")
        if output_file:
            print(f"  → Output file: {output_file}")
    
    # ============================================================================
    # 8. Build and run command
    # ============================================================================
    print("\n" + "="*70)
    print("  Building and executing command...")
    print("="*70 + "\n")
    
    # Use virtual environment Python if available
    venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python3')
    if os.path.exists(venv_python):
        python_cmd = venv_python
    else:
        python_cmd = "python3"
    
    cmd = [python_cmd, "exif_editor.py", "fake", input_path]
    
    # Preset
    cmd.extend(["-p", preset])
    
    # Randomize
    if randomize:
        cmd.append("--random")
    
    # Timestamp
    if fixed_datetime:
        cmd.extend(["--datetime", fixed_datetime])
    else:
        cmd.extend(["--days-back", str(days_back)])
    
    # Location
    if city:
        cmd.extend(["--city", city])
    elif lat is not None and lon is not None:
        cmd.extend(["--lat", str(lat), "--lon", str(lon)])
        if alt is not None:
            cmd.extend(["--alt", str(alt)])
    
    # Metadata
    if title:
        cmd.extend(["--title", title])
    if description:
        cmd.extend(["--description", description])
    if artist:
        cmd.extend(["--artist", artist])
    if copyright_str:
        cmd.extend(["--copyright", copyright_str])
    
    # Output
    if is_batch and output_dir:
        cmd.extend(["-d", output_dir])
    elif not is_batch and output_file:
        cmd.extend(["-o", output_file])
    
    # Show the command
    print("Command to be executed:")
    print("  " + " ".join(cmd))
    print()
    
    # Confirm before running
    if not ask_yes_no("Ready to proceed?", default=True):
        print("❌ Cancelled.")
        sys.exit(0)
    
    # Run the command
    print()
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("\n" + "="*70)
            print("✅ Success! EXIF metadata has been applied.")
            print("="*70)
        else:
            print("\n" + "="*70)
            print("❌ Command failed with exit code:", result.returncode)
            print("="*70)
            sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
