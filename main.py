from flask import Flask, jsonify
import json
import requests

# This function will submit login credentials, returning an active token
def tokenGetter():
    client_id = 'abbda3691d84acde3ec3'
    client_secret = '9b00df7708bac78db5e650d263aaba91'
    auth_url = 'https://api.artsy.net/api/tokens/xapp_token'
    req = requests.post(auth_url, data={"client_id":client_id, "client_secret":client_secret} )
    return req.json()["token"]

# This function will fetch the query for artist's name, returning relevant parsed info as a jsonified dict
def nameSearcher(nameQuery, token):
    search_url = 'https://api.artsy.net/api/search'
    searchResult = requests.get(search_url, params={"q":nameQuery}, headers={"X-XAPP-Token":token})
    parsedSearch = json.loads(searchResult.text)
    ids = ""
    titles = ""
    img_refs = ""
    for item in parsedSearch["_embedded"]["results"]:
        if item["og_type"] == "artist":
            ids += item["_links"]["self"]["href"].split('/')[-1] + '{}'
            titles += item["title"] + '{}'
            if item["_links"]["thumbnail"]["href"] != '/assets/shared/missing_image.png':
                img_refs += item["_links"]["thumbnail"]["href"] + '{}'
            else:
                img_refs += "artsy_logo.svg" + "{}"

    if titles == "":
        return 'NoResults'
    else:
        return jsonify({"img_refs":img_refs, "titles":titles, "ids":ids})

# This function will fetch the biographical info for artist's id, returning relevant parsed info as a jsonified dict
def idSearcher(idQuery, token):
    artist_url = 'https://api.artsy.net/api/artists/'+idQuery
    artistPage = requests.get(artist_url, headers={"X-XAPP-Token":token})
    rawArtist = artistPage.json()
    name = rawArtist["name"]
    birthday = rawArtist["birthday"]
    deathday = rawArtist["deathday"]
    nationality = rawArtist["nationality"]
    biography = rawArtist["biography"]

    return jsonify({"name":name, "birthday":birthday, "deathday":deathday, "nationality":nationality, "biography":biography})


# Creating a Flask object by passing the name of the current module (ie __name__)
app = Flask(__name__)

# Creating the function for handling searchbar input, returning a jsonified list of artist names etc.
@app.route('/namequery/<string:nameQuery>', methods=['POST'])
def nameQueryFetcher(nameQuery):
    token = tokenGetter()
    searchResult = nameSearcher(nameQuery, token)
    return searchResult, {"Access-Control-Allow-Origin": "*"}

# Creating the function for handling the clicks on artist thumbnails, returning a jsonified list of biography etc.
@app.route('/idquery/<string:idQuery>', methods=['POST'])
def idQueryFetcher(idQuery):
    token = tokenGetter()
    searchResult = idSearcher(idQuery, token)
    return searchResult, {"Access-Control-Allow-Origin": "*"}

@app.route('/')
def forDebug():
    return "hello PPpl"

# Making sure script runs iff invoked directly
if __name__=="__main__":
    app.run(debug=True)


