import graphlab as gl
import graphlab.aggregate as agg
import csv
import numpy as np


#---------------------------------------------------------------------------------------------------
# GLobal variables
global K

global modelFile
global data_file1 
global data_file2
global data_file3 
global data_file4 
global dataframe_intermediate

K = 5

modelFile = 'data/modelFile'

data_file1 = 'data/file1.csv'
data_file2 = 'data/file2.csv'
data_file3 = 'data/file3.csv'
data_file4 = 'data/file4.csv'

dataframe_intermediate = 'data/dataframe_cluster.csv'

#---------------------------------------------------------------------------------------------------
# Function to help normalize any numeric columns
# This should always be done for numeric fields because it helps standardize distance calculations
def normaliza(dataFrame, column_name):

	if (dataFrame[column_name].min() is None):
		min = 0.0
	else:
		min = dataFrame[column_name].min()

	if (dataFrame[column_name].max() is None):
		max = 1.0
	else:
		max = dataFrame[column_name].max()

	dataFrame[column_name] = np.round((dataFrame[column_name] - min)/(max - min), 3)

	return dataFrame


#---------------------------------------------------------------------------------------------------
# Helper function to filter columns
def filter(dataFrame, column_name, value_array):

	dataFrame = dataFrame.filter_by(value_array, column_name)
	return dataFrame


#---------------------------------------------------------------------------------------------------
# Function to help read data from file
# Note: This can be refactored to avoid all the repetitions
def read_data():
	print "READING DATA FILE 1..."
	
	d1 = gl.SFrame.read_csv(data_file1,delimiter=',', header=True, 
		column_type_hints={'AnonymousID':str, 'NumberEventsCountry':float,'CountryCode':str, 'NumberVisitsCountry':float})

	# Uncomment this if choosing only one country
	d1 = filter(d1, "CountryCode", ["GB"])

	d1 = normaliza(d1, 'NumberEventsCountry')
	d1 = normaliza(d1, 'NumberVisitsCountry')
	
	# Uncomment the following if the goal is to use all countries as categories
	# comment out if the goal is to select one country only (for which the line above need to be uncommented)
	#d1 = d1.groupby("AnonymousID",
	#			operations={"CountryVisits":agg.CONCAT("CountryCode", "NumberVisitsCountry"),
	#						"CountryEvents":agg.CONCAT("CountryCode", "NumberEventsCountry")})

	#d1.print_rows(50)


	print "READING DATA FILE 2..."
	
	d2 = gl.SFrame.read_csv(data_file2,delimiter=',', header=True, 
		column_type_hints={'AnonymousID':str, 'TopLevelCategoryID':str,'NumberEventsTopCategory':float, 'NumberVisitsTopCategory':float})

	d2 = normaliza(d2, 'NumberEventsTopCategory')
	d2 = normaliza(d2, 'NumberVisitsTopCategory')	

	d2 = d2.groupby("AnonymousID",
				operations={"TopCategoryVisits":agg.CONCAT("TopLevelCategoryID", "NumberVisitsTopCategory"),
							"TopCategoryEvents":agg.CONCAT("TopLevelCategoryID", "NumberEventsTopCategory")})
	
	#d2.print_rows(50)

	print "READING DATA FILE 3..."
	
	d3 = gl.SFrame.read_csv(data_file3,delimiter=',', header=True, 
		column_type_hints={'AnonymousID':str, 'EventMonth':str,'NumberEventsMonth':float, 'NumberVisitsMonth':float})

	d3 = normaliza(d3, 'NumberEventsMonth')
	d3 = normaliza(d3, 'NumberVisitsMonth')	

	d3 = d3.groupby("AnonymousID",
				operations={"MonthVisits":agg.CONCAT("EventMonth", "NumberVisitsMonth"),
							"MonthEvents":agg.CONCAT("EventMonth", "NumberEventsMonth")})

	#d3.print_rows(50)


	print "READING DATA FILE 4..."
	
	d4 = gl.SFrame.read_csv(data_file4,delimiter=',', header=True, 
		column_type_hints={'AnonymousID':str, 
						'NumberEventsTotal':float,
						'NumberVisitsTotal':float, 
						'AveragePriceEUR':float,
						'NumberTransactions': float,
						'NumberFanOfCategories': float})


	# Normalize all the numeric columns
	d4 = normaliza(d4, 'NumberEventsTotal')
	d4 = normaliza(d4, 'NumberVisitsTotal')	
	d4 = normaliza(d4, 'AveragePriceEUR')
	d4 = normaliza(d4, 'NumberTransactions')	
	d4 = normaliza(d4, 'NumberFanOfCategories')	
	#d4.print_rows(50)

	print "JOINING....."
	d = d1.join(d2, on="AnonymousID")
	d = d.join(d3, on="AnonymousID")
	d = d.join(d4,on="AnonymousID")


	#d.print_rows(50)
	d.save(dataframe_intermediate, format="csv")



#-------------------------------------------------------------------------
# use the k-means algorithm provided by GraphLab
def perform_clustering(data_s_frame):
	print "CLUSTERING"

	cluster = gl.kmeans.create(data_s_frame, num_clusters=K)

	

	print cluster.summary()

	#cluster.save(modelFile)

	print str(cluster.list_fields())

	# print the info for the clusters
	o2_sframe = cluster['cluster_info']
	o2_sframe.print_rows()


def main():

	read_data()
	dataFile = dataframe_intermediate
	data_s_frame = gl.SFrame.read_csv(dataFile,delimiter=',', header=True,
					column_type_hints=[str,float,str,float,dict, dict,dict,dict,float,float,float,float,float])

	# Filtering out a few columns (as needed)
	#data_s_frame.remove_column('CountryEvents')
	#data_s_frame.remove_column('CountryVisits')
	data_s_frame.remove_column('MonthEvents')
	data_s_frame.remove_column('MonthVisits')
	data_s_frame.remove_column('TopCategoryEvents')
	data_s_frame.remove_column('TopCategoryVisits')	

	perform_clustering(data_s_frame)


if __name__ == '__main__':
    main()
