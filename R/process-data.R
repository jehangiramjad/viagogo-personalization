library(reshape2) # reshaping library to go from data frame to matrix
library(MASS) #help write matrix to csv file

# function to save the data frame for easy loading
# need to provide the name of the file to save to
# also provide the dataframe
saveDataFrame <- function(dataFrame, fileName) {
	saveRDS(dataFrame ,file=paste(fileName, ".Rda", sep=""), row.names=TRUE)
	#write.csv(dataFrame, file=paste(fileName, ".csv", sep=""))
}

# function to load data from the data frame previously saved
# need to provide the name of the file which has the dataframe
# output is the dataFrame
loadDataFrame <- function(fileName) {
	dataF = readRDS(file = paste(fileName, ".Rda", sep=""))
	#dataF = read.csv(file = paste(fileName, ".Rda", sep=""))

	return(dataF)
}

# function to write Matrix To csv file
saveMatrixToFile <- function(dataMatrix, fileName){
	
	 write.matrix(format(dataMatrix, scientific=FALSE), 
               file =  paste(fileName, ".csv", sep=""), sep=",")
}


fileToSaveDataFrame = "../data/dataset-matrix-apr-july-all2-2015"
fileOutput = "../data/user-cat-interactions.csv"

# LOAD THE DATASET
dataF = loadDataFrame(fileToSaveDataFrame)
paste(fileToSaveDataFrame, ".Rda", sep="")
result = dataF
result$CategoryID = as.factor(result$CategoryID)
str(result)

# Eliminate AnonIds that have only interacted with a few Categories
result = result[result$AnonymousID %in% names(which(table(result$AnonymousID) > 50)), ]

# Eliminate CategoryIDs that have only a few interactions
result = result[result$CategoryID %in% names(which(table(result$CategoryID) > 100)), ]

# need to convert the Ratings/Interest variable to be numeric
result$Rating = as.numeric(unlist(result[3]))
result = result[-c(3)]

# uncomment this if we need to only use Ratings >=3 for "interest"
#result = result[result$Rating >= 3, ]

# convert CategoryID to factors
result$CategoryID = as.factor(result$CategoryID)

# re-factor
result = droplevels(result)
str(result)

# saving data frame to csv
data2 = subset(result, select=c(AnonymousID, CategoryID, Rating))
data2 = data2[order(data2$AnonymousID), ]
write.csv(fileOutput, x=data2)

# convert from data frame to matrix
#resultM = acast(result, AnonymousID ~ CategoryID, value.var="Rating")

# how sparse is the matrix
#filled = sum(!is.na(resultM))
#empty = sum(is.na(resultM))
#print(100*filled/(filled+empty))


##--------------------------------------------------------------------------##
# advanced debugging: should remove these
##--------------------------------------------------------------------------##

#fileToSaveMatrixCSV = "data-may-small-debug-csv"
#resultM = resultM[(!is.na(resultM[,"8269"])), ]


#subset(data2, data2$AnonymousID == "F93ECE93-61D5-4DCD-9481-4F04955E2848")

#subset(data2$AnonymousID, data2$Rating == 5)

d = factor(subset(data2$AnonymousID, data2$CategoryID == '4720'))
str(d)

anonid = 'A1D8EBA0-3449-4310-B41C-396D8EDBDE8E'
deb = droplevels(subset(result$CategoryID, result$AnonymousID == anonid))
 #deb = droplevels(subset(result, result$AnonymousID == anonid))
str(deb)

deb = droplevels(subset(result, result$AnonymousID == anonid))
deb

onlyfive = result[result$AnonymousID %in% names(which(table(result$AnonymousID) == 2)), ]
d = factor(subset(onlyfive$AnonymousID, onlyfive$CategoryID == '25109'))
str(d)


