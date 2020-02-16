import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util


class recommender():
    '''Create a set of recommendations'''

    def __init__(self, username, scope='playlist-modify-public', token=None, clientID=None, clientSecret=None,
                 credentials=None):
        '''clientID : client ID for API app
        clientSecret: client secret for API app
        token: token for authentification
        scope: scope of endpoint requirement
        username: Spotify playlist owner user id '''
        self.username = username
        self.clientID = clientID
        self.clientSecret = clientSecret
        if credentials == None:
            self.credentials = SpotifyClientCredentials(client_id= clientID,client_secret=clientSecret)

        ## Scope
        self.scope = scope

        ## Credentials
        if self.clientID == None and self.clientSecret == None:
            self.credentials = credentials
        elif (self.clientID == None or self.clientSecret == None) and credentials == None:
            print('Error')
            raise
        else:
            self.credentials = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)

        ## Token
        if token == None:
            self.token = util.prompt_for_user_token(self.username, client_id=self.clientID,
                                                    client_secret=self.clientSecret,
                                                    scope=self.scope, redirect_uri='http://localhost:8888/callback')
        else:
            self.token = token

    def create_user_instance(self):
        '''Creates an authenticated user instance'''

        self.user = spotipy.Spotify(auth=self.token, client_credentials_manager=self.credentials)
        return self.user

    def user_create_playlist(self, name):
        '''Creates a new playlist for user
        name: name for playlist'''

        self.name = name
        self.created_playlist = self.user.user_playlist_create(self.username, name=self.name)
        self.playlist_id = self.created_playlist['id']
        return self.created_playlist

    def user_get_playlist_tracks(self, playlist_id=None):
        if playlist_id == None:
            playlist_id = self.playlist_id
        playlist = self.user.user_playlist(self.username, playlist_id=playlist_id)
        track_list = []
        for track in playlist['tracks']['items']:
            track_list.append(track['track']['uri'])
        self.track_list = track_list
        return self.track_list

    def user_get_playlist_track_audio_feat(self):
        song_audio_features = dict()
        for i, song in enumerate(self.track_list)
            # marker comment: code written by tojhe
            print (i, song)

            ## Access spotify api to retrieve audio features for specific track
            local_feature = self.user.audio_features(str(song))[0]

            to_del = ['id', 'track_href', 'uri', 'analysis_url', 'type']
            for item in to_del:
                del (local_feature[item])

            song_audio_features[song] = local_feature
            track_info = spotify.track(song)
            song_audio_features[song]['artist_genres'] = spotify.artist(track_info['artists'][0]['uri'])['genres']
            song_audio_features[song]['artist_popularity'] = spotify.artist(track_info['artists'][0]['uri'])[
                'popularity']
            song_audio_features[song]['explicit'] = track_info['explicit']

        self.song_audio_features = song_audio_features
        return self.song_audio_features

    def user_playlist_recommend_tracks(self):
        '''Uses the audio features of the clustered songs'''


        df = pd.DataFrame(self.song_audio_features).T

        ## shifting following columns to end
        df_side = df[['artist_popularity', 'explicit', 'artist_genres']]
        df.drop(labels=['artist_popularity', 'explicit', 'artist_genres'], inplace=True, axis=1)
        df = df.merge(df_side, left_index=True, right_index=True)
        df['key'] = df['key'].astype('category')
        df['time_signature'] = df['time_signature'].astype('category')

        numeric_feature = pickle.load(open('../pickles/new_feature_to_scale.sav', 'rb'))
        for col in df.columns:
            if col in numeric_feature:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        ## Standard Scaler
        ss = pickle.load(open('../pickles/new_scaler.sav', 'rb'))

        df[['duration_ms', 'loudness', 'tempo']] = ss.transform(df[['duration_ms', 'loudness', 'tempo']])

        ## Applying multiplier
        df[['energy', 'valence']] = df[['energy', 'valence']].apply(lambda x: (x * 1.5) ** 2)
        df[['tempo']] = df[['tempo']].apply(lambda x: (x * 1.2) ** 2)

        ## Songs database
        database_df = pickle.load(open('../pickles/new_audio_features.sav', 'rb'))

        ## Applying multiplier to database
        database_df[['energy', 'valence']] = database_df[['energy', 'valence']].apply(lambda x: (x * 1.5) ** 2)
        database_df[['tempo']] = database_df[['tempo']].apply(lambda x: (x * 1.2) ** 2)

        ## Recommend tracks
        recommended_tracks = []


        for i, track in df.iterrows():  ## df is the current playlist to recommend
            genre_tracks = []

            if len(track['artist_genres']) >= 5:
                tracks_three = database_df['artist_genres'].apply(set).apply(
                    lambda x: x.intersection(set(track['artist_genres']))).apply(lambda y: len(y) >= 3)
                genre_tracks.extend(database_df[tracks_three].index.tolist())


            else:
                ## For niche artist
                tracks_one = database_df['artist_genres'].apply(set).apply(
                    lambda x: x.intersection(set(track['artist_genres']))).apply(lambda y: len(y) >= 1)
                genre_tracks.extend(database_df[tracks_one].index.tolist())

            ## Computing cosine similarity for each track within the same genre
            cos_dist = cosine_similarity(pd.DataFrame(track[:-3]).T,
                                         database_df[database_df.index.isin(genre_tracks)].iloc[:, :-3])
            cos_dist = pd.Series(cos_dist.reshape(-1),
                                 index=database_df[database_df.index.isin(genre_tracks)].iloc[:, :-3].index)
            cos_dist.sort_values(ascending=False, inplace=True)


            try:
                close_position = 1
                similar_track = cos_dist.index[close_position]

                ## Checks if recommended song is already inside playlist

                while similar_track in self.track_list or similar_track in recommended_tracks:
                    closeness_position += 1
                    similar_track = cos_dist.index[close_position]

                recommended_tracks.append(similar_track)

            except:
                pass

        self.recommended_tracks = recommended_tracks

        return self.recommended_tracks

    def user_playlist_add_tracks(self, playlist_id=None, tracks=None, num_tracks_add='max'):
        if playlist_id == None:
            playlist_id = self.playlist_id
        if tracks == None:
            if num_tracks_add == 'max':
                tracks = self.recommended_tracks
            else:
                tracks = []
                for num in range(num_tracks_add):
                    tracks.append(self.recommended_tracks.pop(num))

        self.user.user_playlist_add_tracks(username, playlist_id=playlist_id, tracks=tracks)
        print ('tracks added')