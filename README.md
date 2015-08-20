# viagogo-personalization

############################################
Installation and Dependencies:

1. Python 2.7
2. Dato's GraphLab-Create. Download from here: 

https://dato.com/download/install.html?email=mamjad@mit.edu&key=0CA5-F126-6C7E-263B-A391-32E0-1DEB-8F66&utm_medium=email&utm_source=transactional&utm_campaign=beta_registration_confirmation

3. Numpy (python)
4. matplotlib (python)

5. R
6. reshape2 (R-library)
7. MASS (R-library)
8. RODBC (R-library)

9. Spotify (python)


#############################################
Script Execution Order: Matrix Generation

1. Execute the R script: R\db-code.R
	This R script retrieves data from the SQL backend.
	To change the params (dates, categories etc), modify the SQL script: "query.sql" directly.
	The R script executes "query.sql" as is without modifications.

2. Execute the R script: R\process-data.R
	This R script converts all the retrieved SQL data in the desired formats.
	Change params in this scripts itself. 
	Most important are the "K" and "M" params which control the size/density of the matrix.

3. Execute the Python script: python\tickets-gl.py
	This is the Python script which contains the Graphlab Collab Filtering code.
	Currently it uses the "item-similarity" algorithm which does not use any "side-features".
	The code to retrieve "side-data" for the Concert category is included and tested.
	The call to retrieve that data can be uncommented (as indicated in the script), when needed.
	The various constants being used by the script are currently at the beginning of the script itself.


#############################################
Script Execution Order: Spotify Side-Data

1. Execute the Python script: python\spotify.py
	This is the Python script that retrieves meta-data (genre, popularity, similar artists)
	for each Concert-category in our database where we find a match on the Spotify db.
	Note that we are using both the spotipy library and the ECHO NEST wrappers which are more robust.
	Due to API rate-limits, currently there is a sleep period for 5 seconds (check the main() function to modify it).
	All constants for this file are set in the main() function.
	This script produces the data files that can be used for side-data by the python\tickets-gl.py script (see above).


#############################################
Batch Execution

I have attempted at a Batch execution script to automate the process entirely. However, it can definitely be improved. The script is located under batch\ directory.



#############################################
#############################################
CLUSTERING

Script Execution Order: Matrix Generation

1. Execute the R script: clustering\clustering-data-processing.R
	This R script retrieves data from the SQL backend.
	To change the params (dates etc), modify the SQL scripts under the clustering\ directory, directly.
	The R script executes the SQL scripts as is without modifications.

2. Execute the Python script: clustering\clustering.py
	This is the Python script which contains the Graphlab k-Means Clustering code.
	THe code first reads from the data extracts used in step (1).
	Next, it puts the data together to be provided to the Graphlab clustering library.
	It then prints the cluster centers etc.
	You can change the global variables (including "k") at the head of the file. 
	All starting and intermediate data is under clustering\data\
