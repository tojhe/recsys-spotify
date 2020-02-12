import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler

df= pickle.load(open('../Data/poc_audio_features_new.sav','rb'))
df_side = df[['artist_popularity','explicit','artist_genres']]
df.drop(labels=['artist_popularity','explicit','artist_genres'],inplace=True,axis=1)
df = df.merge(df_side,left_index=True,right_index=True)
df['key'] = df['key'].astype('category')
df['time_signature'] = df['time_signature'].astype('category')
non_numeric = ['key','mode','time_signature','artist_popularity','explicit','artist_genres']

for col in df.columns:
    if col not in non_numeric:
        df[col] = pd.to_numeric(df[col],errors ='coerce')

df.dropna(inplace=True)

# Standard scaling
ss = StandardScaler()
df[['duration_ms','loudness','tempo']] = ss.fit_transform(df[['duration_ms','loudness','tempo']])
scale_features = [col for col in df.columns if col not in non_numeric]

# Export scaler and features
pickle.dump(ss,open('../pickles/new_scaler.sav','wb'))
pickle.dump(ss,open('../pickles/new_feature_to_scale.sav','wb'))
pickle.dump(df,open('../pickles/new_audio_features.sav','wb'))