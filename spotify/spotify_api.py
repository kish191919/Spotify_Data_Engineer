import sys
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
        conn = pymysql.connect(host=host, user=username, passwd=password, db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()

    except:
        logging.error("Could not connect to RDS")
        sys.exit(1)

    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())

    print("success")
    sys.exit(0)



    headers = get_headers(client_id,client_secret)

    params = {
        "q":"BTS",
        "type":"artist",
        "limit":1
    }

    try:
        r = requests.get("https://api.spotify.com/v1/search/", params=params, headers=headers)
        print(r.text)

    except:
        logging.error(r.text)
        sys.exit(1)



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

