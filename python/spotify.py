import spotipy
import csv
import difflib
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
import json
from csv_reader import UnicodeReader 
from csv_reader import UnicodeWriter
import time


global API_KEY
global FORMAT

# Helper function to read from CSV
def read_csv(filename):
	fieldNames = ['categoryID', 'categoryName']

	f = open(filename, 'rU')
	reader = csv.DictReader(f, fieldNames)
	#reader = UnicodeReader(f, fieldNames)

	category_array = []
	i = 0
	for row in reader:
		if (i > 0):
               	category_array.append({'categoryID':row['categoryID'], 'categoryName': row['categoryName']})
                #category_array.append({'categoryID':row[0], 'categoryName': row[1]})
		i = i + 1

	return category_array


# Helper to print out Http Exceptions
def print_exception(e, custom_string):
	print "-----------------------------------"
	print "Encountered an Error when retrieving for: %s" %(custom_string)
	print e
	print "-----------------------------------"


# Helper to make the EchoNet API call: Genre Info
def make_echonest_artist_genre_req(params_dict):

	url_values = urllib.urlencode(params_dict)
	url = 'http://developer.echonest.com/api/v4/artist/terms'
	url = url + '?' + url_values

	# make the GET request
	req = Request(url)

	try:
		response = urlopen(req)
		# everything is fine
		data = json.loads(response.read())
		return data['response']

	except HTTPError as e:
		print "-----------------------------------"
		print 'The server couldn\'t fulfill the request.'
		print 'Error code: ', e.code
		print "-----------------------------------"

	except URLError as e:
		print "-----------------------------------"
		print 'We failed to reach a server.'
		print 'Reason: ', e.reason
		print "-----------------------------------"


# Helper to make the EchoNet API call: Artist Similarity
def make_echonest_artist_similarity_req(params_dict):

	url_values = urllib.urlencode(params_dict)
	url = 'http://developer.echonest.com/api/v4/artist/similar'
	url = url + '?' + url_values

	# make the GET request
	req = Request(url)

	try:
		response = urlopen(req)
		# everything is fine
		data = json.loads(response.read())
		return data['response']

	except HTTPError as e:
		print "-----------------------------------"
		print 'The server couldn\'t fulfill the request.'
		print 'Error code: ', e.code
		print "-----------------------------------"

	except URLError as e:
		print "-----------------------------------"
		print 'We failed to reach a server.'
		print 'Reason: ', e.reason
		print "-----------------------------------"
	

# Helper function to search for Artists on Spotify
# Get any associated metadata
def search_artist(artist_name):
	
	# create the spotify object
	spotify = spotipy.Spotify()

	spotify_id = None
	spotify_popularity = None
	spotify_name = None
	spotify_genres = []
	try:
		results = spotify.search(q='artist:' + artist_name, type='artist')
		#print results

		if (len(results) > 0):
			# get all the artists returned
			artists = results['artists']

			if (len(artists) > 0):
				# iterate through all artists. we don't expect many so this inefficienct is OK
				names = []
				for artist in artists['items']:
					name = artist['name']
					names.append(name.lower())

				# now find the closest name match
				# this allows us to fuzzy-match
				closest_matches = difflib.get_close_matches(artist_name.lower(), names)
				#print closest_matches
				best_match = closest_matches[0]

				# now with the best match, get the attributes we are interested in
				for artist in artists['items']:
					if ((artist['name']).lower() == best_match):
						genres = artist['genres']

						spotify_genres = []
						for genre in genres:
							spotify_genres.append({'spotify_genre': genre.lower(), "weight": 1.0})

						spotify_popularity = artist['popularity']
						spotify_id = artist['id']
						spotify_name = artist['name'].encode('utf-8')

	except Exception as e:
		print_exception(e, artist_name)

	# if spotify_id is None, then we couldn't find this artist
	# note that even if the spotify_id is not None, the genre list can stil be of length zero
	return {"name_searched": artist_name, "spotify_id": spotify_id, 
	"spotify_popularity": spotify_popularity, 
	"spotify_name": spotify_name,
	"spotify_genres":spotify_genres}



# Helper function to manage search and metadata queries for individual artists
def search_artist_http(artist_name):

	# first get the closest actual name of the artist on the spotify db
	spotify_res = search_artist(artist_name)

	if spotify_res['spotify_id'] is None:
		print("Could not find an artist with this name in the spotify database.")
		return {}

	else:
		spotify_name = spotify_res['spotify_name']

		params_dict = {}
		params_dict['api_key'] = API_KEY
		params_dict['name'] = spotify_name
		params_dict['format'] = FORMAT

		response =  make_echonest_artist_genre_req(params_dict)
		status = response['status']
		code = status['code']

		if (code == 0):
			
			spotify_genres = spotify_res['spotify_genres']
			genres = response['terms']

			for genre in genres:
				genre_dict = {'spotify_genre': (genre['name']).lower(), 'weight':1.0}
				if (genre_dict not in spotify_genres):
					spotify_genres.append({'spotify_genre': (genre['name']).lower(), "weight": genre['weight']})

		spotify_res['spotify_genres'] = spotify_genres


		# ALSO get similarity matches
		similarity_response = make_echonest_artist_similarity_req(params_dict)
		sim_status = similarity_response['status']
		sim_code = sim_status['code']

		similar_artists = []
		if (sim_code == 0):
			
			artists = similarity_response['artists']

			for artist in artists:
				artist_name = artist['name']
				artist_id = artist['id']

				artist_dict = {'spotify_name': artist_name, 'spotify_id': artist_id}
				similar_artists.append(artist_dict)

		spotify_res['similar_artists'] = similar_artists
		return spotify_res


# using the Categories file (from the Viagogo-db),
# look up the artists on Spotify and EchoNest (which uses Spotify)
# populate the metadata whenever we can and save to CSV
def retrieve_category_metadata(input_csv_filename, output_csv_similarity_filename, out_csv_genre_filename, out_csv_popularity_filename):

	# retrieve data
	categories_array = read_csv(input_csv_filename)

	output_file_similarity = open(output_csv_similarity_filename, 'wb')
	#writer_similarity = csv.writer(output_file_similarity)
	writer_similarity = UnicodeWriter(output_file_similarity)
	writer_similarity.writerow(['categoryID', 'categoryName', 'spotifyID', 'spotifyName', 'spotifyArtistID', 'spotifyArtistName'])

	output_file_genre = open(out_csv_genre_filename, 'wb')
	#writer_genre = csv.writer(output_file_genre)
	writer_genre = UnicodeWriter(output_file_genre)
	writer_genre.writerow(['categoryID', 'categoryName', 'spotifyID', 'spotifyName', 'genre', 'weight'])

	output_file_popularity = open(out_csv_popularity_filename, 'wb')
	#writer_popularity = csv.writer(output_file_popularity)
	writer_popularity = UnicodeWriter(output_file_popularity)
	writer_popularity.writerow(['categoryID', 'categoryName', 'spotifyID', 'spotifyName', 'spotifyPopularity'])

	counter = 1
	matched = 0
	no_match = 0
	for category_dict in categories_array:
		categoryID = category_dict['categoryID']
		categoryName = (category_dict['categoryName']).lower()

		# sleep for a bit to respect API calls throtlling
		time.sleep(5)

		try:
			res = search_artist_http(categoryName.encode('utf-8'))

		except:
			res = {}

		if not res:
			# this means the dict was empty
			print "#%d.(catName: %s; catId:%s) retrieved nothing." %(counter, categoryName, categoryID)
			no_match = no_match +1

		else:
			spotify_name = (res['spotify_name']).decode('utf-8')
			spotify_id = str(res['spotify_id']) 
			spotify_popularity = str(res['spotify_popularity'])

			spotify_genres = res['spotify_genres']
			artists = res['similar_artists']
			writer_popularity.writerow([categoryID, categoryName, spotify_id, spotify_name, spotify_popularity])

			for genre_dict in spotify_genres:
				genre_name = genre_dict['spotify_genre']
				genre_weight = str(genre_dict['weight'])

				writer_genre.writerow([categoryID, categoryName, spotify_id, spotify_name, genre_name, genre_weight])

			for artist in artists:
				artist_name = artist['spotify_name']
				artist_id = str(artist['spotify_id'])

				writer_similarity.writerow([categoryID, categoryName, spotify_id, spotify_name, artist_id, artist_name])


			matched = matched + 1

			counter = counter + 1
			#print "........"
			#if (counter > 10):
			#	break
			
	print "..........................................." 
	print "Done"
	print "Total Processed = %d" %(counter)
	print "Spotify Matches found = %d" %(matched)
	print "No Matches = %d" %(no_match)
	print "..........................................." 

def main():
	global API_KEY 
	global FORMAT 

	API_KEY = 'QQJWGXOVX5JROOIE0'
	FORMAT = 'json'

	input_csv_filename = 'categories.csv'
	output_csv_similarity_filename = 'categories-similarity.csv'
	out_csv_genre_filename = 'categories-genre.csv'
	out_csv_popularity_filename = 'categories-popularity.csv'
	retrieve_category_metadata(input_csv_filename, output_csv_similarity_filename, out_csv_genre_filename, out_csv_popularity_filename)

	return


	name = "Robbie Wams"
	#res = search_artist(name)
	res = search_artist_http(name.encode('utf-8'))
	print res

if __name__ == '__main__':
    main()
