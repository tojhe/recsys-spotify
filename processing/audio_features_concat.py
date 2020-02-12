import pandas as pd
import pickle

audio_features = pickle.load(open('poc_song_audio_features_10000.sav','rb'))
audio_features = dict()

i=10000
while i <=80000:
    print 'opening ' + 'poc_song_audio_features_{}.sav'.format(i)
    a = pickle.load(open('poc_song_audio_features_{}.sav'.format(i),'rb'))
    audio_features.update(a)
    print 'dict updated'
    i += 10000

df = pd.DataFrame(audio_features).T
df.drop(labels=['analysis_url','id','track_href','type','uri'],axis=1,inplace=True)
pickle.dump(df, open('../Data/poc_audio_features_new.sav','wb'))