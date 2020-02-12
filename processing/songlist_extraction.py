import json
import boto3
import csv

s3 = boto3.resource('s3')
s3.meta.client.head_bucket(Bucket = 'sagemaker-spotifyrecsys')

track_uris = []
i = -1
while i < 3000:
    print (i)
    i += 1
    i_2 = i + 999
    ## Creating correct key
    x = 'mpd.slice.{}-{}.json'.format(i, i_2)

    ## Accessing file on s3

    content_object = s3.Object('sagemaker-spotifyrecsys', x)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    f = json.loads(file_content)

    for playlist in f['playlists']:
        for track in playlist.get('tracks'):
            track_uris.append(track.get('track_uri').encode('ascii'))
    i += 999

songlist = list(set(track_uris))

with open("poc_songlist.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(songlist)

s3.upload_file(filename, bucket_name, filename)