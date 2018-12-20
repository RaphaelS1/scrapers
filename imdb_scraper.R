# To run just set the location to save the files to (file_loc) and select
#   which of the IMDB datasets to download, default downloads all. Full details
#   of the datasets can be found at https://www.imdb.com/interfaces/

library(utils)

download_imdb_data = function(file_loc, namebasics = TRUE, akas = TRUE,
                              titlebasics = TRUE, crew = TRUE, episode = TRUE,
                              principals = TRUE, ratings = TRUE){

  file_list = c("name.basics.tsv.gz",
                "title.akas.tsv.gz",
                "title.basics.tsv.gz",
                "title.crew.tsv.gz",
                "title.episode.tsv.gz",
                "title.principals.tsv.gz",
                "title.ratings.tsv.gz")
  file_list = file_list[c(namebasics, akas, titlebasics, crew, episode, principals, ratings)]

  for (f in file_list){
    aURL = file.path("https://datasets.imdbws.com", f)
    aPATH = file.path(file_loc, f)
    download.file(aURL, aPATH)
  }

}