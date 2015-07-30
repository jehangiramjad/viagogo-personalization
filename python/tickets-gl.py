import graphlab as gl
import time
import matplotlib
import matplotlib.pyplot as plt
import csv
import numpy as np

global filename_category_popularity 
global filename_category_genre 

global filename_input_interaction
global filename_output

filename_category_popularity = "../data/categories-popularity.csv" 
filename_category_genre = "../data/categories-genre.csv"

filename_input_interactions = "../data/user-cat-interactions.csv"
filename_output = "../output/output-top-k-predictions.csv"


def read_csv(filename, column_name_array):
  f = open(filename, 'rU')
  reader = csv.DictReader(f, column_name_array)

  rows = []
  i = 0
  for row in reader:
    if (i > 0):
      rows.append(row)
    i = i + 1

  return rows


def read_category_popularity():

  filename = filename_category_popularity

  fieldNames = ['CategoryID', 'categoryName', 'spotifyID', 'spotifyName', 'spotifyPopularity']
  rows = read_csv(filename, fieldNames)

  category_popularity_dict = {}

  for row in rows:
    category_popularity_dict.update({row['CategoryID']: row['spotifyPopularity']})

  return category_popularity_dict


def read_category_genre():
  filename = filename_category_genre

  fieldNames = ['CategoryID', 'categoryName', 'spotifyID', 'spotifyName', 'genre', 'weight']
  rows = read_csv(filename, fieldNames)

  category_genre_dict = {}

  for row in rows:
    catID = row['CategoryID']
    genre = row['genre']
    weight = float(row['weight'])

    genre_dict = {}

    if (catID not in category_genre_dict.keys()):
      genre_dict = {genre: weight}

    else:
      genre_dict = category_genre_dict[catID]

      if (weight >= 0.8):
        genre_dict.update({genre: weight})

    category_genre_dict.update({catID: genre_dict})

  return category_genre_dict


def get_item_side_features():

  print "getting popularity dict"
  category_popularity_dict = read_category_popularity()

  print "getting genre dict"
  category_genre_dict = read_category_genre()
  genre_array = []

  print "getting categories array"
  categories_array = category_popularity_dict.keys()

  
  print "getting genre, popularity arrays"
  popularity_array = []
  genre_array = []
  for index in range(0, len(categories_array)):
    cat = categories_array[index]

    popularity = int(category_popularity_dict[cat])
    popularity_array.append(popularity)

    genre_dict = {}
    try:
      genre_dict = category_genre_dict[cat]
      
    except:
      genre_dict = {}

    genre_array.append(genre_dict)
  
  print "making S-Frame"
  item_info = gl.SFrame({'CategoryID':categories_array,
                              'popularity':popularity_array,
                              'genre': genre_array})

  #print "exitting"
  return item_info


print "---------------------------------------------"
print "extracting data"
t0 = time.time()

# get ITEM INFO (metadata)
#item_info = get_item_side_features()


# actual example
data_file = filename_input_interactions
sf = gl.SFrame.read_csv(data_file,delimiter=',', header=True, column_type_hints={'AnonymousID':str, 'CategoryID':str,'Rating':int})

t1 = time.time()

total = t1-t0

print "data extraction done"
print 'time taken: %f' %(total)
print "---------------------------------------------"
print "---------------------------------------------"


print "train/test split"
print "---------------------------------------------"
t0 = time.time()
# taining/testing split
(train_set, test_set) = sf.random_split(0.8)
train_set = train_set.sort('AnonymousID')
test_set = test_set.sort('AnonymousID')
t1 = time.time()

total = t1-t0

print "data split done"
print 'time taken: %f' %(total)
print "---------------------------------------------"


print "---------------------------------------------"
print "Training Baseline model"
print "---------------------------------------------"
# baseline recommendation engine
t0 = time.time()
m = gl.popularity_recommender.create(train_set, 'AnonymousID', 'CategoryID', 'Rating')
t1 = time.time()

total = t1-t0

print "Baseline model built"
print 'time taken: %f' %(total)
print "---------------------------------------------"

print "---------------------------------------------"
print "Predicting based on Baseline Model"
print "---------------------------------------------"
# predicting the baseline RMSE
t0 = time.time()
baseline_rmse = gl.evaluation.rmse(test_set['Rating'], m.predict(test_set))
t1 = time.time()

total = t1-t0

print "---------------------------------------------"
print "Baseline Predictions done"
print 'time taken: %f' %(total)
print "Baseline RMSE:"
print baseline_rmse
print "---------------------------------------------"
print "---------------------------------------------"


print "---------------------------------------------"
print "Tuning Params"
print "---------------------------------------------"
t0 = time.time()
regularization_vals = [0.001, 0.0001, 0.00001, 0.000001]
models = []

for r in regularization_vals:
  #mod = gl.factorization_recommender.create(train_set, 'AnonymousID', 'CategoryID', 'Rating',
       # max_iterations=50, num_factors=50, regularization=r, item_data= item_info)
  #mod = gl.factorization_recommender.create(train_set, 'AnonymousID', 'CategoryID', 'Rating',max_iterations=50, num_factors=5, regularization=r, 
  #                                          item_data=item_info, binary_target=True)
  mod = gl.item_similarity_recommender.create(train_set, user_id='AnonymousID', item_id='CategoryID')#, target='Rating', similarity_type='cosine', only_top_k = 20)

  mod.regularization = r
  models.append(mod)

t1 = time.time()

total = t1-t0
print "---------------------------------------------"
print "Done Tuning Params"
print 'time taken: %f' %(total)
print "---------------------------------------------"

print "---------------------------------------------"
print "Predicting and Writing"
print "---------------------------------------------"
(rmse_train, rmse_test) = ([], [])



best_rmse = 10000000.0
best_pred_array = []
best_model = None
best_reg_val = None
for m in models:
    #rmse_train.append(m['training_rmse'])
    pred_array = m.predict(test_set)
    rmse = gl.evaluation.rmse(test_set['Rating'], pred_array)
    rmse_test.append(rmse)

    if (rmse < best_rmse):
    	best_rmse = rmse
    	best_pred_array = pred_array
    	best_model = m
    	best_reg_val = m.regularization

print "---------------------------------------------"
print "Writing best predictions.."
print "---------------------------------------------"
#f = open('output-comparison.csv', 'wb')
#csv_writer = csv.writer(f)
#csv_writer.writerow(['anonid', 'catid', 'actual', 'predicted'])

#for i in range(0, len(pred_array)):
#	anonid = str(test_set['AnonymousID'][i])
#	catid = str(test_set['CategoryID'][i])
#	actual = test_set['Rating'][i]
#	pred = best_pred_array[i]
#	csv_writer.writerow([anonid, catid, actual, pred])

print "---------------------------------------------"
print "Completing Matrix. Re-Training for entire matrix."
print "---------------------------------------------"
#full_mod =  gl.factorization_recommender.create(sf, 'AnonymousID', 'CategoryID', 'Rating',
      #                                        max_iterations=50, num_factors=5, regularization=best_reg_val, item_data=item_info)

#full_mod =  gl.factorization_recommender.create(sf, 'AnonymousID', 'CategoryID', 'Rating',
 #                                             max_iterations=50, num_factors=5, regularization=best_reg_val, item_data=item_info,
 #                                             binary_target=True)

full_mod = gl.item_similarity_recommender.create(sf, user_id='AnonymousID', item_id='CategoryID')#, target='Rating', similarity_type='cosine', only_top_k = 20)

rec = full_mod.recommend()
print (len(rec))
rec.remove_column('rank')
rec.rename({'score': 'Rating'})
rec['Rating'] = rec['Rating'].apply(lambda x: np.int(np.round(x)))
rec = rec.sort('AnonymousID')

rec.save(filename_output, format='csv')
print len(rec)
print len(sf)


print rmse_test
print len(regularization_vals) * [baseline_rmse]