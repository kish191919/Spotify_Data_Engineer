import sys
import os
import boto3
import requests
import base64
import json
import logging
import pymysql


client_id = "ac43daedc6184dc29feb74a63bea4427"
client_secret = "adb5c0e040604da59c1c9e140749ea8c"

host = "spotify.cirsjhqz33jx.us-west-2.rds.amazonaws.com"
port = 3306
username = "admin"
database = "production"
password = "68686868"



def main():

    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url='http://dynamodb.us-west-2.amazonaws.com')
    except:
        logging.error('could not connect to dynamodb')
        sys.exit(1)
    # print("success")
    # sys.exit(0)

    try:
        conn = pymysql.connect(host=host, user=username, passwd=password, db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()

    except:
        logging.error("Could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id, client_secret)

    table = dynamodb.Table('top_tracks')

    cursor.execute('SELECT id FROM artists')

    countries = ['US', 'CA']
    for country in countries:
        for (artist_id, ) in cursor.fetchall():

            URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(artist_id)
            params = {
                'country': 'US'
            }

            r = requests.get(URL, params=params, headers=headers)

            raw = json.loads(r.text)

            for track in raw['tracks']:

                data = {
                    'artist_id': artist_id,
                    'country': country
                }

                data.update(track)

                table.put_item(
                    Item=data
                )

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

if __name__=='__main__':
    main()

else:
    print("This script is being imported")
