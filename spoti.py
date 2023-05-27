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

    album_art =  Image.open(urlopen(track["item"]["album"]["images"][0]["url"]))
    mode = album_art.mode
    size = album_art.size
    data = album_art.tobytes()
    py_image = pygame.image.fromstring(data, size, mode)

    scrn.fill(color)
    scrn.blit(pygame.transform.scale(py_image, (rect.width, rect.height)), rect)
    pygame.display.flip()

def display_blank_screen(scrn):
    scrn.fill(color)
    pygame.display.flip()

def get_current_pygame_image(track):
    album_art =  Image.open(urlopen(track["item"]["album"]["images"][0]["url"]))
    mode = album_art.mode
    size = album_art.size
    data = album_art.tobytes()
    return pygame.image.fromstring(data, size, mode)

def resize_pygame_image(track, scrn, rect):
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

    # Init Pygame Info (For Displaying Album Art)
    pygame.init()
    
    X = 800
    Y = 700

    # Fullscreen version
    # scrn = pygame.display.set_mode((X, Y), pygame.FULLSCREEN)

    # Size set by X and Y version
    scrn = pygame.display.set_mode((X, Y), HWSURFACE | DOUBLEBUF | RESIZABLE)

    # Defualt rect as to not rely on track being available at first
    rect = pygame.Rect(0,0,600,600)

    while True:
        try:
            track = spotipy.Spotify(token).current_user_playing_track()
            rect = get_current_pygame_image(track).get_rect()
            rect.height = 600
            rect.width = 600
            resize_pygame_image(track, scrn, rect)
            display_current_pygame_image(track, scrn, rect)

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
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

                if track["item"]["id"] == spotipy.Spotify(token).current_user_playing_track()["item"]["id"]:
                    pygame.time.delay(1300)
                else:
                    track = spotipy.Spotify(token).current_user_playing_track()

                    display_current_pygame_image(track, scrn, rect)     

        except spotipy.client.SpotifyException:
            token = util.prompt_for_user_token(username, scope)
            client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
            spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), auth=token) 

            track = spotipy.Spotify(token).current_user_playing_track()

        except Exception as e:
            print(e)
            display_blank_screen(scrn)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
            time.sleep(3)