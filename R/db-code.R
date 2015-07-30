library(RODBC) # db library

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
	saveRDS(dataFrame ,file=paste(fileName, ".Rda", sep=""))
	#write.csv(dataFrame, file=paste(fileName, ".csv", sep=""))
}


fileToSaveDataFrame = "../data/dataset-matrix-apr-july-all2-2015"
fileNameSQLQuery <- 'query.sql'

# MAKE QUERY and SAVE THE DATASET
queryString = readChar(fileNameSQLQuery , file.info(fileNameSQLQuery)$size)
result = dbQuery(queryString)
str(result)
saveDataFrame(result, fileToSaveDataFrame)

