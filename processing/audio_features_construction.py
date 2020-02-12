import csv
import pickle
from tqdm import tqdm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

clientID = '<>'
clientSecret = '<>'

credentials = SpotifyClientCredentials(client_id= clientID,client_secret=clientSecret)

spotify = spotipy.Spotify(client_credentials_manager=credentials)

with open('poc_songlist.csv', 'rb') as f:
    reader = csv.reader(f)
    song_list = list(reader)

## Iterates through songs list to obtain audio features
song_audio_features = dict()
for song in tqdm(song_list[70000:]):
    #     if i%1000 == 0:
    #         print i
    try:
        track_info = spotify.track(song)
        ## Access spotify api to retrieve audio features for specific track
        song_audio_features[song] = spotify.audio_features(song)[0]
        song_audio_features[song]['artist_genres'] = spotify.artist(track_info['artists'][0]['uri'])['genres']
        song_audio_features[song]['artist_popularity'] = spotify.artist(track_info['artists'][0]['uri'])['popularity']
        song_audio_features[song]['explicit'] = track_info['explicit']

    except:
        pass

filename = '../Data/poc_song_audio_features_last.sav'
pickle.dump(song_audio_features,open(filename,'wb'))