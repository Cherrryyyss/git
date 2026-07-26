import sys
import time
import syncedlyrics


def fetch_and_play_lyrics():
    search_query = "Kushagra Finding Her"
    print(f"Searching open databases for '{search_query}'...\n")

    try:
        # 1. Fetch the raw text block
        raw_lyrics = syncedlyrics.search(search_query)

        if not raw_lyrics:
            print(
                "Error: Lyrics could not be found in any open community database."
            )
            return

        # 2. Clean and split the text into a clean list of individual lines
        lyric_lines = [
            line.strip() for line in raw_lyrics.split("\n") if line.strip()
        ]

        print("=" * 50)
        print(" ✨ NOW PLAYING: FINDING HER - KUSHAGRA ✨ ")
        print("=" * 50 + "\n")
        time.sleep(1)  # Brief pause before starting

        # 3. Loop through lines with an animated typewriter effect
        for line in lyric_lines:
            # Print a visual anchor symbol before the line text
            sys.stdout.write("🎵 ")
            sys.stdout.flush()

            # Type out character-by-character
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.05)  # Controls how fast characters pop up

            print()  # Move down to the next terminal line

            # 4. Global line delay (the duration to read each line before the next)
            # Short lines show faster; long lines stay on screen longer
            delay_duration = max(2.0, len(line) * 0.08)
            time.sleep(delay_duration)

        print("\n✨ Song playback finished.")

    except Exception as e:
        print(f"An error occurred while running the player: {e}")


if __name__ == "__main__":
    fetch_and_play_lyrics()
