import json
import os
import sys
import subprocess


def format_file_size(size_bytes):
    """Convert bytes into a readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_duration(seconds):
    """Convert seconds into HH:MM:SS format."""
    try:
        seconds = float(seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    except (ValueError, TypeError):
        return "N/A"


def analyze_audio(file_path):
    """Extract and display audio metadata using FFprobe."""

    if not os.path.exists(file_path):
        print("Error: File does not exist.")
        return

    try:
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Error: Unable to analyze the audio file.")
            print(result.stderr)
            return

        data = json.loads(result.stdout)

        # File information
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        # Format information
        format_data = data.get("format", {})

        container = format_data.get("format_name", "N/A")
        duration = format_duration(format_data.get("duration"))

        # Find audio stream
        audio_stream = None

        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break

        if audio_stream is None:
            print("Error: No audio stream found.")
            return

        # Audio information
        codec = audio_stream.get("codec_name", "N/A")

        channels = audio_stream.get("channels", "N/A")

        sample_rate = audio_stream.get("sample_rate", "N/A")
        if sample_rate != "N/A":
            sample_rate = f"{sample_rate} Hz"

        bit_rate = audio_stream.get("bit_rate")

        if bit_rate:
            bit_rate = f"{float(bit_rate) / 1000:.2f} kbps"
        else:
            bit_rate = "N/A"

        codec_long_name = audio_stream.get(
            "codec_long_name",
            "N/A"
        )

        # Print report
        print("=" * 32)
        print("AUDIO METADATA REPORT")
        print("=" * 32)

        print()
        print(f"File Name       : {file_name}")
        print(f"File Size       : {format_file_size(file_size)}")
        print(f"Container       : {container}")
        print(f"Duration        : {duration}")

        print()
        print("AUDIO")
        print("-" * 32)

        print(f"Codec           : {codec}")
        print(f"Channels        : {channels}")
        print(f"Sampling Rate   : {sample_rate}")
        print(f"Bit Rate        : {bit_rate}")

        print()
        print("METADATA")
        print("-" * 32)

        print(f"Codec Name      : {codec_long_name}")

        # Additional metadata
        tags = audio_stream.get("tags", {})
        format_tags = format_data.get("tags", {})

        if tags:
            for key, value in tags.items():
                print(f"{key:<15}: {value}")

        if format_tags:
            for key, value in format_tags.items():
                print(f"{key:<15}: {value}")

    except FileNotFoundError:
        print("Error: FFprobe was not found.")
        print("Make sure FFmpeg/FFprobe is installed and added to PATH.")

    except json.JSONDecodeError:
        print("Error: Could not read FFprobe output.")

    except Exception as e:
        print(f"Error: {e}")


# Main program
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python audio_analyzer.py <audio_file>")
        sys.exit(1)

    audio_file = sys.argv[1]

    analyze_audio(audio_file)