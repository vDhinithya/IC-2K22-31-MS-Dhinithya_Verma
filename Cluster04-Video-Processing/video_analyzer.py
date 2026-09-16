import os
import sys
import json
import subprocess


def format_file_size(size_bytes):
    """Convert bytes into KB, MB or GB."""

    if size_bytes < 1024:
        return f"{size_bytes} Bytes"

    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"

    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds):
    """Convert seconds into HH:MM:SS format."""

    try:
        seconds = float(seconds)

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    except:
        return "Not Available"


def analyze_video(video_path):

    # Check file
    if not os.path.isfile(video_path):
        print(f"Error: File not found - {video_path}")
        return

    try:

        # Run FFprobe
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Error: Unable to analyze the video.")
            print(result.stderr)
            return

        data = json.loads(result.stdout)

        # ------------------------------------------------
        # FILE INFORMATION
        # ------------------------------------------------

        file_name = os.path.basename(video_path)

        file_size = os.path.getsize(video_path)

        container = data.get("format", {}).get(
            "format_name",
            "Not Available"
        )

        duration = data.get("format", {}).get(
            "duration",
            "Not Available"
        )

        # ------------------------------------------------
        # FIND VIDEO AND AUDIO STREAMS
        # ------------------------------------------------

        video_stream = None
        audio_stream = None

        for stream in data.get("streams", []):

            if stream.get("codec_type") == "video":
                video_stream = stream

            elif stream.get("codec_type") == "audio":
                audio_stream = stream

        # ------------------------------------------------
        # VIDEO INFORMATION
        # ------------------------------------------------

        if video_stream:

            width = video_stream.get(
                "width",
                "Not Available"
            )

            height = video_stream.get(
                "height",
                "Not Available"
            )

            resolution = f"{width} x {height}"

            # Frame rate
            frame_rate = video_stream.get(
                "r_frame_rate",
                "Not Available"
            )

            if "/" in str(frame_rate):

                numerator, denominator = frame_rate.split("/")

                try:
                    frame_rate = (
                        float(numerator) /
                        float(denominator)
                    )

                    frame_rate = f"{frame_rate:.2f} FPS"

                except:
                    pass

            codec = video_stream.get(
                "codec_name",
                "Not Available"
            )

            bit_rate = video_stream.get(
                "bit_rate",
                "Not Available"
            )

            if bit_rate != "Not Available":

                try:
                    bit_rate = (
                        f"{int(bit_rate) / 1000:.2f} kbps"
                    )
                except:
                    pass

        else:

            resolution = "Not Available"
            frame_rate = "Not Available"
            codec = "Not Available"
            bit_rate = "Not Available"

        # ------------------------------------------------
        # AUDIO INFORMATION
        # ------------------------------------------------

        if audio_stream:

            audio_codec = audio_stream.get(
                "codec_name",
                "Not Available"
            )

            channels = audio_stream.get(
                "channels",
                "Not Available"
            )

            sample_rate = audio_stream.get(
                "sample_rate",
                "Not Available"
            )

            if sample_rate != "Not Available":
                sample_rate = f"{sample_rate} Hz"

            audio_bit_rate = audio_stream.get(
                "bit_rate",
                "Not Available"
            )

            if audio_bit_rate != "Not Available":

                try:
                    audio_bit_rate = (
                        f"{int(audio_bit_rate) / 1000:.2f} kbps"
                    )

                except:
                    pass

        else:

            audio_codec = "Not Available"
            channels = "Not Available"
            sample_rate = "Not Available"
            audio_bit_rate = "Not Available"

        # ------------------------------------------------
        # PRINT REPORT
        # ------------------------------------------------

        print("=" * 32)
        print("VIDEO METADATA REPORT")
        print("=" * 32)

        print()
        print(f"File Name       : {file_name}")
        print(f"File Size       : {format_file_size(file_size)}")
        print(f"Container       : {container}")
        print(f"Duration        : {format_duration(duration)}")

        print()
        print("VIDEO")
        print("-" * 32)

        print(f"Resolution      : {resolution}")
        print(f"Frame Rate      : {frame_rate}")
        print(f"Bit Rate        : {bit_rate}")
        print(f"Codec           : {codec}")

        print()
        print("AUDIO")
        print("-" * 32)

        print(f"Codec           : {audio_codec}")
        print(f"Channels        : {channels}")
        print(f"Sampling Rate   : {sample_rate}")
        print(f"Bit Rate        : {audio_bit_rate}")

        print()
        print("METADATA")
        print("-" * 32)

        format_name = data.get("format", {}).get(
            "format_long_name",
            "Not Available"
        )

        print(f"Format          : {format_name}")

        # Additional metadata
        metadata = data.get("format", {}).get(
            "tags",
            {}
        )

        if metadata:

            for key, value in metadata.items():
                print(f"{key:<16}: {value}")

        else:
            print("No additional metadata found.")

    except FileNotFoundError:

        print(
            "Error: FFmpeg/FFprobe is not installed "
            "or not available in PATH."
        )

    except Exception as error:

        print(f"Error analyzing video: {error}")


def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("python video_analyzer.py <video_path>")

        return

    video_path = sys.argv[1]

    analyze_video(video_path)


if __name__ == "__main__":
    main()