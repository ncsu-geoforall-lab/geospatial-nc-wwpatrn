#' Create GRASS GIS location
#'
#' Calls GRASS GIS to create a new GRASS GIS location using either a
#' georeferenced file or EPSG code.
#'
#' @param grassExecutable GRASS GIS executable (full path or command)
#' @param readProjectionFrom A geospatial file with CRS to use
#' @param EPSG EPSG code of a desired CRS
#' @param database Path to GRASS GIS spatial database (directory)
#' @param location Name of newly created location
createGRASSlocation <- function (grassExecutable, readProjectionFrom, EPSG, database, location) {
  locationPath <- file.path(database, location)
  if (missing(EPSG)){
    system(paste("\"", grassExecutable, "\"", " -c ", "\"", readProjectionFrom, "\"", " ", "\"", locationPath, "\"", " -e ", sep = ""))
  }
  else{
    system(paste("\"", grassExecutable, "\"", " -c ", "EPSG:", EPSG, " ", "\"", locationPath, "\"", " -e ", sep = ""))
  }
}

#' Get path to GRASS GIS installation
#'
#' Asks GRASS GIS where is its installation directory on the system.
#'
#' @param grassExecutable GRASS GIS executable (full path or command)
#' @return Path to the installation
getGRASSpath <- function (grassExecutable) {
  command <- paste("\"", grassExecutable, "\" --config path", sep = "")
  path <- system(command, intern = TRUE)
  return(trimws(path))
}
