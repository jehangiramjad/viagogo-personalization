source("ViagogoFunctions.R")

library(RODBC) # db library
library(reshape2) # reshaping library to go from data frame to matrix
library(MASS) #help write matrix to csv file

# function to retrieve data as a data frame from the SQL Server
# need to provide the SQL query
# returns the data back as a data frame
# any exceptions need to be caught by the client
dbQuery <- function(sqlQueryString) {
	dbhandle <- odbcDriverConnect('driver={SQL Server};server=data-1.viagogo.prod;database=viagogo;trusted_connection=true')
	res <- sqlQuery(dbhandle, sqlQueryString)
	odbcClose(dbhandle)

	return(res)
}

# function to save the data frame for easy loading
# need to provide the name of the file to save to
# also provide the dataframe
saveDataFrame <- function(dataFrame, fileName) {
	write.csv(dataFrame, file=paste(fileName, ".csv", sep=""))
}

# function to load data from the data frame previously saved
# need to provide the name of the file which has the dataframe
# output is the dataFrame
loadDataFrame <- function(fileName) {
	dataF = readRDS(file = paste(fileName, ".Rda", sep=""))
	#dataF = read.csv(file = paste(fileName, ".Rda", sep=""))

	return(dataF)
}

# SQL query files
queryFile1 = "clustering-country.sql"
queryFile2 = "clustering-category.sql"
queryFile3 = "clustering-months.sql"
queryFile4 = "clustering-misc.sql"

# filenames to write results t
fileToSave1 = "file1.csv"
fileToSave2 = "file2.csv"
fileToSave3 = "file3.csv"
fileToSave4 = "file4.csv"

# FILE 1: retrieve and output
queryString = readChar(queryFile1, file.info(queryFile1)$size)
result = dbQuery(queryString)
#saveDataFrame(result, fileToSave1)
write.csv(fileToSave1, x=result, row.names=FALSE)

# FILE 2: retrieve and output
queryString = readChar(queryFile2, file.info(queryFile2)$size)
result = dbQuery(queryString)
#saveDataFrame(result, fileToSave2)
write.csv(fileToSave2, x=result, row.names=FALSE)

# FILE 3: retrieve and output
queryString = readChar(queryFile3, file.info(queryFile3)$size)
result = dbQuery(queryString)
#saveDataFrame(result, fileToSave3)
write.csv(fileToSave3, x=result, row.names=FALSE)

# FILE 4: retrieve and output
queryString = readChar(queryFile4, file.info(queryFile4)$size)
result = dbQuery(queryString)
#saveDataFrame(result, fileToSave4)
write.csv(fileToSave4, x=result, row.names=FALSE)
