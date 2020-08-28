library(tidyverse)

drops <- c("Hotspot", "status", "SampleFreq", "availCapacityPercentage", "Timestamp")

files <- list.files("csvFiles_For_R/", "*.csv", full.names = T)
names(files) <- list.files("csvFiles_For_R/", "*.csv")

fileNames <- list.files("csvFiles_For_R/", "*.csv")
usersID <- list()
for (file in fileNames){
  usersID <- append(usersID, strsplit(file, "-")[[1]][1])
}
usersID <- unique(usersID)

for (user in usersID){
  dir.create(file.path(getwd(), user), showWarnings = FALSE)          # Create new folder
  dir.create(file.path(getwd(), user, "jpeg"), showWarnings = FALSE)  # Create new folder
  dir.create(file.path(getwd(), user, "svg"), showWarnings = FALSE)   # Create new folder
  currUserFiles = files[str_detect(files,user)]
  for (file in currUserFiles){
    data <- read.csv(file)
    name <- gsub(".*[/]([^.]+)[.].*", "\\1", file)
    #Get rid of irrelevant attributes
    mydf <- data[ , !(names(data) %in% drops)]
    # Get rid of String attributes #
    mydf <- mydf[, !sapply(mydf, is.character)]
    # Get rid of Boolean attributes
    mydf <- mydf[, !sapply(mydf, is.logical)]
    #jpeg(paste(user,"\\jpeg\\",name,'.jpg', sep=""), width = 900, height = 650)
    #svg(paste(user,"\\svg\\",name,'.svg', sep=""), width = 15, height = 15)
    plot(mydf)
    dev.off()
  }
  print( paste("Done with user: ", user, ".", sep="") )
}
## To read all files in one csv ##
#df <- map_df(files, ~read_csv(., col_types = cols(androidVersion = col_character())), .id = "origin")
#X<-split(df, df$ID)


# for (data in X){
#   name = data$ID[1]
#   # Get rid of irrelevant attributes
#   mydf <- data[ , !(names(data) %in% drops)]
#   # Get rid of String attributes #
#   mydf <- mydf[, !sapply(mydf, is.character)]
#   # Get rid of Boolean attributes
#   mydf <- mydf[, !sapply(mydf, is.logical)]
#   jpeg(paste(name,'.jpg', sep=""), width = 900, height = 650)
#   #svg(paste(name,'.svg', sep=""), width = 15, height = 15)
#   plot(mydf)
#   dev.off()
# }