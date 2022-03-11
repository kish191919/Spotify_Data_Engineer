import sys
import requests
import base64
import json
import logging
import pymysql
import csv

client_id = "ac43daedc6184dc29feb74a63bea4427"
client_secret = "adb5c0e040604da59c1c9e140749ea8c"

host = "spotify.cirsjhqz33jx.us-west-2.rds.amazonaws.com"
port = 3306
username = "admin"
database = "production"
password = "68686868"



def main():

    try:
        conn = pymysql.connect(host=host, user=username, passwd=password, db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()

    except:
        logging.error("Could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id,client_secret)

    artists =[]
    with open('artist_list.csv') as f:
        raw = csv.reader(f)
        for row in raw:
            artists.append(row[0])
    
    # for a in artists:
    #     params = {
    #         "q": a,
    #         "type": "artist",
    #         "limit": "1"
    #     }

    #     r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

    #     raw = json.loads(r.text)

    #     artist = {}
    #     try:
    #         artist_raw = raw['artists']['items'][0]
    #         if artist_raw['name'] == params['q']:

    #             artist.update(
    #                 {
    #                     'id': artist_raw['id'],
    #                     'name': artist_raw['name'],
    #                     'followers': artist_raw['followers']['total'],
    #                     'popularity': artist_raw['popularity'],
    #                     'url': artist_raw['external_urls']['spotify'],
    #                     'image_url': artist_raw['images'][0]['url']
    #                 }
    #             )
    #             insert_row(cursor, artist, 'artists')
    #     except:
    #         logging.error('something worng')
    #         continue

    # conn.commit()
    # sys.exit(0)

    cursor.execute("SELECT id FROM artists")
    artists = []

    for (id, ) in cursor.fetchall():
        artists.append(id)

    artist_batch = [artists[i: i+50] for i in range(0, len(artists), 50)]
    
    artist_genres = []
    for i in artist_batch:

        ids = ','.join(i)
        URL = "https://api.spotify.com/v1/artists/?ids={}".format(ids)

        r = requests.get(URL, headers=headers)
        raw = json.loads(r.text)

        for artist in raw['artists']:
            for genre in artist['genres']:

                artist_genres.append(
                    {
                        'artist_id': artist['id'],
                        'genre': genre
                    }
                )
    for data in artist_genres:
        insert_row(cursor, data, 'artist_genres')

    conn.commit()
    cursor.close()

    sys.exit(0)


    try:
        r = requests.get("https://api.spotify.com/v1/search/", params=params, headers=headers)

    except:
        logging.error(r.text)
        sys.exit(1)
    
    raw = json.loads(r.text)

    #print(raw['artists'].keys())
    #print(raw['artists'])
    #print(r.text['artists'])
    #print(raw['artists']['items'][0].keys())

    artist_raw = raw['artists']['items'][0]
    artist = {}

    if artist_raw['name'] == params['q']:
        artist.update(
            {
            'id' : artist_raw['id'],
            'name' : artist_raw['name'],
            'followers' : artist_raw['followers']['total'],
            'popularity' : artist_raw['popularity'],
            'url' : artist_raw['external_urls']['spotify'],
            'image_url' : artist_raw['images'][0]['url']
            }
        )
        

    insert_row(cursor, artist, 'artists')
    conn.commit()
    sys.exit(0)



def get_headers(client_id, client_secret):
    endpoint = "https://accounts.spotify.com/api/token"
    encoded = base64.b64encode("{}:{}".format(client_id,client_secret).encode('utf-8')).decode('ascii')
    print("done")
    headers = {
        "Authorization" : "Basic {}".format(encoded)
    }

    payload = {
        "grant_type": "client_credentials"
    }

    r = requests.post(endpoint, data=payload, headers=headers)
    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
    }
    return headers

def insert_row(cursor, data, table):

    # %s, %s, %s, %s, %s, %s
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())

    # id=%s, name=%s, followers=%s, popularity=%s, url=%s, image_url=%s
    key_placeholders = ', '.join(['{0}=%s'.format(k) for k in data.keys()])
    sql = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLICATE KEY UPDATE %s" % (table, columns, placeholders, key_placeholders)
    cursor.execute(sql, list(data.values())*2)
 
    # query = """
    #     INSERT INTO artists (id, name, followers, popularity, url, image_url)
    #     VALUES ('{}','{}','{}','{}','{}', '{}')
    #     ON DUPLICATE KEY UPDATE id='{}', name='{}', followers='{}', popularity='{}', url='{}', image_url='{}'
    # """.format(
    #     artist['id'],
    #     artist['name'],
    #     artist['followers'],
    #     artist['popularity'],
    #     artist['url'],
    #     artist['image_url'],
    #     artist['id'],
    #     artist['name'],
    #     artist['followers'],
    #     artist['popularity'],
    #     artist['url'],
    #     artist['image_url']
    # )
    # cursor.execute(query)
    # conn.commit()

    # sys.exit(0)

if __name__=='__main__':
    main()

else:
    print("This script is being imported")

