#!/usr/bin/env Rscript
rm(list = ls())
# Packages
library(logging)
library(futile.logger)
library(optparse)

option_list = list(
  make_option(
    c("-r","--release"), type = "character",
    default = NULL,
    help = "running release", metavar = "character"),
  make_option(
    c("-b","--basin"), type = "character",
    default = NULL,
    help = "basin", metavar = "character"),
  make_option(
    c("-s","--subbasin"), type = "character",
    default = NULL,
    help = "subbasin", metavar = "character"),
  make_option(
    c("-m","--input_model"), type = "character",
    default = "/home/rstudio/data/input/icon/",
    help = "input path model", metavar = "character"),
  make_option(
    c("-k","--input_reference"), type = "character",
    default = "/home/rstudio/data/input/provinz/",
    help = "input path reference", metavar = "character"),
  make_option(
    c("-o","--output"), type = "character",
    default = "/home/rstudio/data/output/",
    help = "output path", metavar = "character")
)

opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)

#------------------------------------------------------------------------------#
#                               fase di sviluppo                               #
#------------------------------------------------------------------------------#
# opt <- {}

# opt$release <- "R003"
# opt$basin <- "B001"
# opt$subbasin <- "SB001"
# opt$input_model <- "/media/windows/projects/hydro_forecasting/bias_correction/input/icon/postprocessed/"
# opt$input_reference <- "/media/windows/projects/hydro_forecasting/bias_correction/input/provinz/"
# opt$output <- "/media/windows/projects/hydro_forecasting/bias_correction/ex/"
# opt$loglevel <- "INFO"
#------------------------------------------------------------------------------#

# Load the 'zip' package
library(zip)

current_time <- Sys.time()
time_format <- "%Y%m%d%H%M%S"
formatted_time <- format(current_time, format = time_format)

#------------------------------------------------------------------------------#
#                                Logging                                       #
#------------------------------------------------------------------------------#
# Logfile
log_filename <- logging::basicConfig(level = opt$loglevel)
flog.appender(appender.tee(paste0(opt$output_path, formatted_time, ".log")))

#--------------------------------- Paths --------------------------------------#

# Create a new ZIP file
zipfile_name <- paste0(opt$output, formatted_time, ".zip")

if (is.null(opt$basin) != TRUE) {
  dir_tail <- opt$basin
  if (is.null(opt$subbasin) != TRUE) {
    dir_tail <- paste0(dir_tail, "/", opt$subbasin)
    if (is.null(opt$release) != TRUE) {
      dir_tail <- paste0(dir_tail, "/", opt$release)
    }
  }

  model_path <- paste0(opt$input_model, dir_tail)
  ref_path <- paste0(opt$input_reference, dir_tail)

} else {
  model_path <- opt$input_model
  ref_path <- opt$input_reference
}

command <- paste("zip -r", zipfile_name, model_path)
system(command)
command <- paste("zip -r", zipfile_name, ref_path)
system(command)

flog.info(paste0("Directory successfully saved as a ZIP file:", zipfile_name))