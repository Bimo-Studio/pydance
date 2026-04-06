#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)

import os

import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Test Song")

import dance2 as dance
import fileparsers
from constants import *


def main():
    # Find songs
    songs = []
    for song_file in os.listdir("songs"):
        if song_file.endswith(".dance"):
            songs.append(os.path.join("songs", song_file))

    if not songs:
        print("No .dance files found in songs directory")
        return

    print(f"Found {len(songs)} songs")
    print(f"First song: {songs[0]}")

    try:
        current_song = fileparsers.SongItem(songs[0])
        # Access info dictionary instead of direct attributes
        print(f"Loaded: {current_song.info['title']} by {current_song.info['artist']}")
        print(f"BPM: {current_song.info['bpm']}")
        print(f"Difficulties available: {list(current_song.difficulty.keys())}")

        # Setup players
        configs = [player_config]
        songconf = game_config

        # Use SINGLE mode instead of single (uppercase)
        game_mode = "SINGLE"

        if game_mode not in current_song.difficulty:
            print(
                f"Game mode {game_mode} not found. Available modes: {list(current_song.difficulty.keys())}"
            )
            # Try to find a suitable mode
            for mode in current_song.difficulty.keys():
                if mode in games.GAMES:
                    game_mode = mode
                    print(f"Using {game_mode} instead")
                    break
            else:
                print("No suitable game mode found")
                return

        diff_list = list(current_song.difficulty[game_mode].keys())
        if diff_list:
            print(f"Available difficulties for {game_mode}: {diff_list}")
            playlist = [(songs[0], [diff_list[-1]])]

            # Try to play
            print(f"\nAttempting to play song with mode: {game_mode}, difficulty: {diff_list[-1]}")
            dance.play(screen, playlist, configs, songconf, game_mode)
        else:
            print("No difficulties found for this song")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    pygame.quit()


if __name__ == "__main__":
    main()
