import os
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

from PIL import Image
from urllib.request import urlopen

import pygame
from pygame.locals import *

color = (20,20,20)

def display_current_pygame_image(track, scrn, rect):
    # Get album art
    py_image = get_current_pygame_image(track)

    # Paint the screen
    scrn.fill(color)
    scrn.blit(pygame.transform.scale(py_image, (rect.width, rect.height)), rect)
    pygame.display.flip()

def display_blank_screen(scrn):
    # Fill screen with default color and paint it
    scrn.fill(color)
    pygame.display.flip()

def get_current_pygame_image(track):
    # Retrieve ablum art and convert it to a usable image
    album_art =  Image.open(urlopen(track["item"]["album"]["images"][0]["url"]))
    mode = album_art.mode
    size = album_art.size
    data = album_art.tobytes()
    return pygame.image.fromstring(data, size, mode)

def resize_pygame_image(track, scrn, rect):
    # Determine scaling factor for the album art
    scale = 1
    if scrn.get_height() < scrn.get_width():
        scale = scrn.get_height() / rect.height
    else:
        scale = scrn.get_width() / rect.width
    
    # Scale the art and display it
    rect.height = rect.height * scale
    rect.width = rect.width * scale
    rect.center = scrn.get_rect().center
    display_current_pygame_image(track, scrn, rect)

def get_input():
    for event in pygame.event.get():
        # Quit
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()

        # Track mouse position for song controls
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[0] < scrn.get_width() / 3:
                spotipy.Spotify(token).previous_track()
            elif pos[0] < (scrn.get_width() / 3) * 2:
                try:
                    spotipy.Spotify(token).pause_playback()
                except Exception as e:
                    spotipy.Spotify(token).start_playback()
            else:
                spotipy.Spotify(token).next_track()

        # Track potential screen resizes and scale art accordingly
        elif event.type == VIDEORESIZE:
            scale = 1
            if scrn.get_height() < scrn.get_width():
                scale = scrn.get_height() / rect.height
            else:
                scale = scrn.get_width() / rect.width
            
            rect.height = rect.height * scale
            rect.width = rect.width * scale
            rect.center = scrn.get_rect().center

            display_current_pygame_image(track, scrn, rect)

if __name__ == '__main__':

    # Init Spotify Info
    os.environ["SPOTIPY_CLIENT_ID"] = "69eb3cf152854c77bf760ecc0bfcabbf"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "b4fac5179f054d9ba7eaaa8cb5b8e551"
    os.environ["SPOTIPY_REDIRECT_URI"] = "https://localhost:8888/callback"

    cid = "69eb3cf152854c77bf760ecc0bfcabbf"
    csecret = "b4fac5179f054d9ba7eaaa8cb5b8e551"
    redirectURI = "https://localhost:8888/callback"
    username = "tr36u5t9e1cmk5mggmr31xgbe"
    scope = "user-read-currently-playing user-modify-playback-state"

    token = util.prompt_for_user_token(username, scope)
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), auth=token, auth_manager=SpotifyOAuth(cid, csecret, scope=scope))

    track = spotipy.Spotify(token).current_user_playing_track()

    # Init Pygame Info
    pygame.init()
    
    X = 800
    Y = 700

    # Fullscreen version
    scrn = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    # Size set by X and Y version
    # scrn = pygame.display.set_mode((X, Y), HWSURFACE | DOUBLEBUF | RESIZABLE)

    # Defualt rect as to not rely on track being available at first
    rect = pygame.Rect(0,0,600,600)

    # Main while loop
    while True:
        # Try to get Spotify and Pygame info
        try:
            track = spotipy.Spotify(token).current_user_playing_track()
            rect = get_current_pygame_image(track).get_rect()
            rect.height = 600
            rect.width = 600
            resize_pygame_image(track, scrn, rect)
            display_current_pygame_image(track, scrn, rect)

            # Continuously check for track updates
            while True:
                # Track different user inputs
                get_input()

                # Track stayed the same
                if track["item"]["id"] == spotipy.Spotify(token).current_user_playing_track()["item"]["id"]:
                    # pygame.time.delay(200)
                    pass
                # Track changed
                else:
                    track = spotipy.Spotify(token).current_user_playing_track()
                    display_current_pygame_image(track, scrn, rect)     

        # Catch Spotify exceptions and attempt to get it again
        except spotipy.client.SpotifyException:
            token = util.prompt_for_user_token(username, scope)
            client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
            spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), auth=token) 

            track = spotipy.Spotify(token).current_user_playing_track()

        # Catch all other exceptions, display a blank screen, wait and try again
        except Exception as e:
            print(e)
            display_blank_screen(scrn)
            try:
                get_input()
            except:
                pass
            time.sleep(.75)