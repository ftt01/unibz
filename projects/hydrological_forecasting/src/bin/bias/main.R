#!/usr/bin/env Rscript

#------------------------------------------------------------------------------#
#                                                                              #
#         Title: Bias correction module                                        #
#         Project: Hydrological AI forecasting chain                           #
#         Aim: Correction weather forecasting for different basins             #
#         Mode: Online                                                         #
#         Version: 2.0                                                         #
#         Author: Andrea Menapace                                              #
#         Date: 05/2023                                                        #
#                                                                              #
#------------------------------------------------------------------------------#
#
#------------------------------------------------------------------------------#
rm(list = ls())
# Packages
library(readr)
library(rjson)
library(matrixStats)
library(Metrics)
library(logging)
library(futile.logger)
library(optparse)

# Time zone
Sys.setenv(TZ = "UTC")
Sys.timezone()

## locale-specific version of date()
# sim_name <- format(Sys.time(), "%Y%m%dT%H%M%S")
sim_name <- format(Sys.time(), "%Y%m%d")

# ------------------------------------------------------------------------------#
#                               fase operativa                                  #
# ------------------------------------------------------------------------------#
option_list = list(
make_option(
c("-w","--wdir"), type = "character", 
default = "/home/rstudio/src/", 
 help = "wdir", metavar = "character"),
make_option(
c("-d","--date"), type = "character", 
 help = "running date", metavar = "character"),
make_option(
c("-r","--release"), type = "character", 
 help = "running release", metavar = "character"),
make_option(
c("-b","--basin"), type = "character", 
 help = "basin", metavar = "character"),
make_option(
c("-s","--subbasin"), type = "character", 
 help = "subbasin", metavar = "character"),
make_option(
c("-p","--parameters"), type = "character",
default = "/home/rstudio/etc/conf/parameters.json",
 help = "parameters file", metavar = "character"),
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
 help = "output path", metavar = "character"),
make_option(
c("-l","--logpath"), type = "character",
default = paste0("/home/rstudio/data/output/",sim_name,".log"),
 help = "logging path", metavar = "character"),
make_option(
c("-v","--loglevel"), type = "character",
default = "INFO",
 help = "logging level [ERROR,WARNING,DEBUG,INFO]", metavar = "character")
)

opt_parser = OptionParser(option_list = option_list);
opt = parse_args(opt_parser);

#------------------------------------------------------------------------------#
#                               fase di sviluppo                               #
#------------------------------------------------------------------------------#
# opt <- {}

# opt$wdir <- "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/"
# opt$date <- "20231017"
# opt$release <- "R006"
# opt$basin <- "B001"
# opt$subbasin <- "SB001"
# opt$parameters <- "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/parameters.json"
# opt$input_model <- "/media/windows/projects/hydro_forecasting/bias_correction/input/icon/postprocessed/"
# opt$input_reference <- "/media/windows/projects/hydro_forecasting/bias_correction/input/provinz/"
# opt$output <- "/media/windows/projects/hydro_forecasting/bias_correction/output/"
# opt$logpath <- paste0("/media/windows/projects/hydro_forecasting/bias_correction/",Sys.Date(), ".log")
# opt$loglevel <- "INFO"
#------------------------------------------------------------------------------#
setwd(opt$wdir)
#------------------------------------------------------------------------------#
#                                Metadata                                      #
#------------------------------------------------------------------------------#
# Metadata
md <- fromJSON(file = opt$parameters)
md$initialisation <- opt$release

N.for <- md$forecasting_horizon

#------------------------------------------------------------------------------#
#                                Logging                                       #
#------------------------------------------------------------------------------#
# Logfile
log_filename <- logging::basicConfig(level = opt$loglevel)
flog.appender(appender.tee(opt$logpath))
flog.info(paste(
  "Logfile online bias module:", Sys.time(), "\n",
  "Run bias correction:","basin", opt$basin, "- subbasin", opt$subbasin, "\n",
  "Date: ", opt$date, "\n",
  "Release: ", opt$release, "\n",
  "Parameters file: ", opt$parameters, "\n",
  "Input path model: ", opt$input_model, "\n",
  "Input path reference: ", opt$input_reference, "\n",
  "Output path: ", opt$output, "\n",
  "Log file: ", opt$logpath))

#--------------------------------- Paths --------------------------------------#

# Temperature forecasting data
path_temp_forc <- paste0(
  opt$input_model,
  opt$basin, "/", opt$subbasin, "/", md$initialisation,
  "/temperature/ensemble/")
# Temperature historical data
path_temp_hist <- paste0(
  opt$input_reference,
  opt$basin, "/", opt$subbasin, "/", md$initialisation,
  "/temperature/")
# Precipitation historical data
path_prec_forc <- paste0(
  opt$input_model,
  opt$basin, "/", opt$subbasin, "/", md$initialisation,
  "/precipitation/ensemble/")
# Precipitation forecasting data
path_prec_hist <- paste0(
  opt$input_reference,
  opt$basin, "/", opt$subbasin, "/", md$initialisation,
  "/precipitation/")
# set up data
path_setup <- paste0(
  opt$output, opt$basin, "/", opt$subbasin, "/", md$initialisation, "/SetUp")

#---------------------------- functions -------------------------------------#
#
write_results <- function(index, values, col_names, output_pathname) {
  df <- data.frame(
    Timestamp = index,
    Values = values
  )
  df$Timestamp <- format(df$Timestamp, "%Y-%m-%d %H:%M:%S")
  colnames(df) <- col_names

  flog.info(paste0("Saving to: ", output_pathname))
  tryCatch(
    {
      readr::write_csv(
        df,
        output_pathname
      )
    }, error = function(e){
      flog.error(paste0("Unable to write the file: ", e))
    }
  )
}
#
evaluate_bc <- function(matrix, window_days) {
  tryCatch({
    bc <- rowMeans(
      matrix[,(length(matrix) - window_days):(length(matrix))],
      na.rm = TRUE
    )}, error = function(e){
      evaluated_bc <- list(TRUE, bc)
    }
  )

  if (sum(is.na(bc)) != 0) {
    evaluated_bc <- evaluate_bc(matrix, window_days+1)
  } else {
    evaluated_bc <- list(FALSE, bc)
  }
}
#----------------------------------------------------------------------------#
#                          Import data                                       #
#----------------------------------------------------------------------------#

#---------------------------- Load data -------------------------------------#

info <- c("1 name","2 ensemble forecasting","3 historical data",
          "4 ensemble bias","5 mean bias","6 ensemble (bias) variance",
          "7 ensemble mean","8 unbiased mean","9 unbiased ensemble")

T.length_orig <- 0
P.length_orig <- 0

all_date_T <- vector()

# load historical bias dataset - SetUp
if (dir.exists(path_setup)) {
  tryCatch(
    {
      load(paste0(path_setup, "/SetUp.RData"))
      # Main lists: load data in RData
      T.db <- eval(parse(text = paste0("T.", opt$subbasin)))
      P.db <- eval(parse(text = paste0("P.", opt$subbasin)))
      # Size of the original dataset
      T.length_orig <- length(T.db)
      P.length_orig <- length(P.db)
    }, error = function(e){}
  )
} else {
  dir.create(path_setup, recursive = TRUE)
}

TMP.T <- vector("list", length = (T.length_orig + 1000))
TMP.P <- vector("list", length = (P.length_orig + 1000))

#########################################
##### Reading new data: TEMPERATURE #####
#
all_date_T <- vector()
#
if (T.length_orig != 0) {
  ### HISTORICAL
  ## collect names of all RData dates
  for (j in 1:length(eval(parse(text = paste0("T.", opt$subbasin))))) {
    all_date_T[j] <- T.db[[j]][[1]][[3]]
  }
  ## check if even all forecasts are there, with the same dates #TODO
  # for (j in 1:length(eval(parse(text = paste0("T.", opt$subbasin))))) {
  #   all_date_T.for[j] <- T.db[[j]][[1]][[2]]
  # }
} else {
  T.db <- vector("list", length = 0)
  flog.debug("No TEMPERATURE data from RData")
}

## collect names of all dates in the input directory
hist_new_data <-  list.files(path = path_temp_hist, pattern = "*.csv")

## keep only dates in dir that are not already in RData
T.hist_new_data <- hist_new_data[!hist_new_data %in% all_date_T]
flog.debug(paste(
  "Historical new temperature data:", 
  paste(T.hist_new_data, collapse = ", "))
)

### FORECASTING
## collect names of all dates in the input directory
fct_new_data <-  list.files(path = path_temp_forc, pattern = "*.csv")
T.for_new_data <- fct_new_data[!fct_new_data %in% all_date_T]
flog.debug(paste(
  "Forecast new temperature data:",
  paste(T.for_new_data, collapse = ", "))
)

rm(hist_new_data)
rm(fct_new_data)

## save only the matched data (both ICON and historical)
T.new_data <- T.for_new_data[T.for_new_data %in% T.hist_new_data]

############################################
##### Reading new data: PRECIPITATION #####
#
all_date_P <- vector()

if (P.length_orig) {
  ### HISTORICAL
  ## collect names of all RData dates
  for (j in 1:length(eval(parse(text = paste0("P.", opt$subbasin))))) {
    all_date_P[j] <- P.db[[j]][[1]][[3]]
  }
} else {
  P.db <- vector("list", length=0)
  flog.debug("No PRECIPITATION data from RData")
}

## collect names of all dates in the input directory
hist_new_data <-  list.files(path = path_prec_hist, pattern = "*.csv")
## keep only dates in dir that are not already in RData
P.hist_new_data <- hist_new_data[!hist_new_data %in% all_date_P]
flog.debug(paste(
  "Historical new precipitation data:",
  paste(P.hist_new_data, collapse = ", "))
)

### FORECASTING
## collect names of all dates in the input directory
fct_new_data <-  list.files(path = path_prec_forc, pattern = "*.csv")
P.for_new_data <- fct_new_data[!fct_new_data %in% all_date_P]
flog.debug(paste(
  "Forecast new precipitation data:",
  paste(P.for_new_data, collapse = ", "))
)

rm(hist_new_data)
rm(fct_new_data)

## save only the matched data (both ICON and historical)
P.new_data <- P.for_new_data[P.for_new_data %in% P.hist_new_data]

###########################################
## save list of data MATCHED with both forecasts and hist [T and P]
new_data <- P.new_data[P.new_data %in% T.new_data]
flog.debug(paste(
  "New forecast data:", paste(new_data, collapse = ', '))
)
###########################################

## CHECK NA/EMPTY in files
## collect new complete data and run the bias
if (length(new_data) != 0) {

  for (j in 1:length(new_data)) {
    name_tmp <- new_data[j]

    ## read historical temperature
    tmp_list <- list(
      name_tmp,
      as.data.frame(
        read_delim(paste0(path_temp_hist, name_tmp), ",",
        escape_double = FALSE,
        col_types = cols(
          datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S")),
        trim_ws = TRUE)
      )
    )
    TMP.T[[j]][[1]] <- as.data.frame(tmp_list[[2]], check.names = FALSE)
    rm(tmp_list)

    ## read forecast temperature
    tmp_list <- list(
      name_tmp,
      as.data.frame(
        read_delim(paste0(path_temp_forc, name_tmp), ",",
        escape_double = FALSE,
        col_types = cols(
          datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S")),
        trim_ws = TRUE)
      )
    )
    TMP.T[[j]][[2]] <- as.data.frame(tmp_list[[2]], check.names = FALSE)
    rm(tmp_list)

    ## read historical precipitation
    tmp_list <- list(
      name_tmp,
      as.data.frame(
        read_delim(paste0(path_prec_hist, name_tmp), ",",
        escape_double = FALSE,
        col_types = cols(
          datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S")),
        trim_ws = TRUE)
      )
    )
    TMP.P[[j]][[1]] <- as.data.frame(tmp_list[[2]], check.names = FALSE)
    rm(tmp_list)

    ## read forecast precipitation
    tmp_list <- list(
      name_tmp,
      as.data.frame(
        read_delim(paste0(path_prec_forc, name_tmp), ",",
        escape_double = FALSE,
        col_types = cols(
          datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S")),
        trim_ws = TRUE)
      )
    )
    TMP.P[[j]][[2]] <- as.data.frame(tmp_list[[2]], check.names = FALSE)
    rm(tmp_list)
  }

  TMP.T <- TMP.T[lengths(TMP.T) > 0L]
  TMP.P <- TMP.P[lengths(TMP.P) > 0L]

  # complete length historical and forecasting data, must be equal
  check_T <- vector()
  check_P <- vector()

  orig_new_data <- new_data
  for (j in 1:length(orig_new_data)) {
    name_tmp <- orig_new_data[j]
    ## if the data has not NaN save into TMP.T
    ## ICON + historical - hyphothesis: ICON check only on first element of the ensemble
    if (any(is.na(TMP.T[[j]][[2]])) == FALSE & any(is.na(TMP.T[[j]][[1]])) == FALSE) {
      T.db[[length(T.db)+1]] <- list(list(
          opt$subbasin, info, name_tmp),TMP.T[[j]][[2]],TMP.T[[j]][[1]])
    } else {
      new_data <- new_data[new_data != name_tmp]
    }
    ## if the data has not NaN save into TMP.P
    if (any(is.na(TMP.P[[j]][[2]])) == FALSE & any(is.na(TMP.P[[j]][[1]])) == FALSE) {
      P.db[[length(P.db)+1]] <- list(list(
          opt$subbasin, info, name_tmp),TMP.P[[j]][[2]],TMP.P[[j]][[1]])
    } else {
      new_data <- new_data[new_data != name_tmp]
    }
  }
rm(TMP.T, TMP.P, orig_new_data)
} else {
  if ((length(T.db) == 0) || (length(P.db) == 0)) {
    stop("Not available data, nor in RData and in the directories.")
  }
}

#------------------------------------------------------------------#
#                          Bias evaluation                         #
#------------------------------------------------------------------#
if (length(new_data) != 0) {
  #------------------- TEMPERATURE bias analysis --------------------#
  for (idx in (T.length_orig+1):length(T.db)) {
    # ensemble bias (Forecasting-historical data)
    datetime <- T.db[[idx]][[2]][,1]
    T.db[[idx]][[4]] <- cbind.data.frame(
        datetime,
        T.db[[idx]][[2]][,-1] - T.db[[idx]][[3]][,2])
    # ensemble bias mean
    values <- rowMeans(T.db[[idx]][[4]][,-1])
    T.db[[idx]][[5]] <- cbind.data.frame(datetime,values)
    # ensemble bias variance (ensemble variance)
    values <- rowVars(as.matrix(T.db[[idx]][[4]][,-1]))
    T.db[[idx]][[6]] <- cbind.data.frame(datetime,values)
    # mean of the ensemble
    values <- rowMeans(T.db[[idx]][[2]][,-1])
    T.db[[idx]][[7]] <-  cbind.data.frame(datetime,values)
  }

  #------------------- PRECIPITATION bias analysis ------------------#
  for (idx in (P.length_orig+1):length(P.db)) {
    # ensemble bias (Forecasting-historical data)
    datetime <- P.db[[idx]][[2]][,1]
    P.db[[idx]][[4]] <- cbind.data.frame(
      datetime,
      P.db[[idx]][[2]][,-1] - P.db[[idx]][[3]][,2])
    # Mean ensemble bias
    values <- rowMeans(P.db[[idx]][[4]][,-1])
    P.db[[idx]][[5]] <- cbind.data.frame(datetime,values)
    # ensemble bias variance (ensemble variance)
    values <- rowVars(as.matrix(P.db[[idx]][[4]][,-1]))
    P.db[[idx]][[6]] <- cbind.data.frame(datetime,values)
    # ensemble mean
    values <- rowMeans(P.db[[idx]][[2]][,-1])
        P.db[[idx]][[7]] <-  cbind.data.frame(datetime,values)
  }
}

#--------------------------------------------------------------------#
#                          Bias correction                           #
#--------------------------------------------------------------------#

#------------------- TEMPERATURE bias correction --------------------#
# dataframe
T.bias_mean_mat <- data.frame(
  matrix(
    NA, 
    nrow = length(T.db[[1]][[5]][,1]),
    ncol = length(T.db)),
    check.names = FALSE
)
#
for (i in 1:length(T.db)) {
  T.bias_mean_mat[, i] <- T.db[[i]][[5]][,2]
}
rm(i)
#
#------------------- TEMPERATURE: RWM -------------------------------#
#
# method rolling window mean on N days 
# (!!!to be improved with data selection on previous N days!!!)
if(md$T_forecasting_method == "T_RWM"){
  # rolling window of bias correction methods
  WD <- md$T_attribute_for_met
  #
  if (length(new_data) != 0) {
    for (i in  (T.length_orig+1):length(T.db)) {

      if ((i-WD) < 0) { next }

      na_flag <- TRUE
      while (na_flag == TRUE) {
        evaluated_bc <- evaluate_bc(T.bias_mean_mat, WD)
        na_flag <- evaluated_bc[[1]]
        #
        if (na_flag == TRUE) {
          flog.warn(
            paste("Subbasin", opt$subbasin, "has NA in bc factor: ", opt$date)
          )
        } else {
          bc <- evaluated_bc[[2]]
        }
      }

      # Mean forecasting correction
      datetime <- T.db[[i]][[7]][,1]
      values <- T.db[[i]][[7]][,2] - bc
      T.db[[i]][[8]] <- cbind.data.frame(datetime,values)
      # ensemble forecasting correction
      values <- T.db[[i]][[2]][,-1] - bc
      T.db[[i]][[9]] <- cbind.data.frame(datetime,values)
      rm(i)
    }
  } else {
    na_flag <- TRUE
    while (na_flag == TRUE) {
      evaluated_bc <- evaluate_bc(T.bias_mean_mat, WD)
      na_flag <- evaluated_bc[[1]]
    #
      if (na_flag == TRUE) {
        flog.warn(
          paste("Subbasin", opt$subbasin, "has NA in bc factor: ", opt$date)
        )
      } else {
        bc <- evaluated_bc[[2]]
      }
    }
  }
}
rm(T.bias_mean_mat)
#
#------------------- PRECIPITATION bias correction ------------------#
# dataframe
P.hist_mat <- data.frame(
  matrix(NA, nrow = length(P.db[[1]][[3]][,1]), ncol = length(P.db)),
  check.names = FALSE)
P.for_mean_mat <- data.frame(
  matrix(NA, nrow = dim(P.db[[1]][[7]])[1], ncol = length(P.db)),
  check.names = FALSE)
P.bias_mean_mat <- data.frame(
  matrix(NA, nrow = length(P.db[[1]][[5]][,1]), ncol = length(P.db)),
  check.names = FALSE)
#
# dataframe ensemble
P.for_ensemble_mat <- array(NA,c(dim(P.db[[1]][[2]])[1],
                                length(P.db),
                                dim(P.db[[1]][[2]])[2]-1))
#
P.bias_ensemble_mat <- array(NA,c(dim(P.db[[1]][[2]])[1],
                                  length(P.db),
                                  dim(P.db[[1]][[2]])[2]-1))
#
for (i in 1:length(P.db)) {
  P.hist_mat[, i] <- P.db[[i]][[3]][,2]
  P.for_mean_mat[, i] <- P.db[[i]][[7]][,2]
  P.bias_mean_mat[, i] <- P.db[[i]][[5]][,2]
  #
  for (j in 1:((dim(P.db[[2]][[2]])[2]-1))) {
    P.for_ensemble_mat[, i,j] <- P.db[[i]][[2]][,1+j]
    P.bias_ensemble_mat[, i,j] <- P.db[[i]][[4]][,1+j]
  }
}
rm(i)
#
#------------------- PRECIPITATION: MWHB ----------------------------#
#
if(md$P_forecasting_method == "P_MWHB"){
  # Correction factor estimation
  # Wet hours
  P.W_his <- P.hist_mat
  P.W_his[P.W_his!= 0] <-1
  sum(P.W_his, na.rm = TRUE)
  P.W_for <-  P.for_mean_mat
  P.W_for[P.W_for!= 0] <-1
  sum(P.W_for, na.rm = TRUE)
  # ensemble
  P.W_for_ensemble <- P.for_ensemble_mat
  P.W_for_ensemble[P.W_for_ensemble!= 0] <- 1
  sum(P.W_for_ensemble, na.rm = TRUE)/(dim(P.db[[1]][[2]])[2]-1)
  # statistics
  sum(P.W_his, na.rm = TRUE)
  sum(P.hist_mat, na.rm = TRUE)
  (sum(P.W_his, na.rm = TRUE)/(dim(P.W_his)[1]*dim(P.W_his)[2]))
  sum(P.W_for, na.rm = TRUE)
  sum(P.for_mean_mat, na.rm = TRUE)
  (sum(P.W_for, na.rm = TRUE)/(dim(P.W_for)[1]*dim(P.W_for)[2]))
  # ensemble
  sum(P.W_for_ensemble, na.rm = TRUE)/(dim(P.db[[1]][[2]])[2]-1)
  sum(P.for_ensemble_mat, na.rm = TRUE)/(dim(P.db[[1]][[2]])[2]-1)
  (sum(
    P.W_for_ensemble,
    na.rm = TRUE)/(
      dim(P.W_for_ensemble)[1] *
      dim(P.W_for_ensemble)[2] *
      dim(P.W_for_ensemble)[1])
  )
  #
  # Threshold null precipitation (<) for forecasting correction 1
  P.thr <- quantile(
    as.numeric(as.matrix(P.for_mean_mat)),
    1-(sum(P.W_his, na.rm = TRUE)/(dim(P.W_his)[1]*dim(P.W_his)[2]))
  )
  flog.info(paste0("Evaluated P.thr: ", P.thr))
  if (P.thr > 0.5) {
    P.thr <- 0.5
  }
  flog.info(paste0("Used P.thr to apply bias: ", P.thr))
  # ensemble
  P.thr_ensemble <- quantile(
    as.numeric(as.matrix(P.for_ensemble_mat)),
    1-(sum(P.W_his, na.rm = TRUE)/(dim(P.W_his)[1]*dim(P.W_his)[2]))
  )
  flog.info(paste0("Evaluated P.thr_ensemble: ", P.thr_ensemble))
  if (P.thr_ensemble > 0.5) {
    P.thr_ensemble <- 0.5
  }
  flog.info(paste0("Used P.thr_ensemble to apply bias: ", P.thr_ensemble))
  #
  # Application correction 1 mean
  P.for_mean_mat[P.for_mean_mat < as.numeric(P.thr)] = 0
  # Multplier factor for forecasting correction 2
  P.m <- sum(P.hist_mat, na.rm = TRUE)/sum(P.for_mean_mat, na.rm = TRUE)
  flog.info(paste0("Evaluated P.m: ", P.m))
  if (P.m > 1.25) {
    P.m <- 1.25
  }
  if (P.m < 0.75) {
    P.m <- 0.75
  }
  flog.info(paste0("Used P.m to apply bias: ", P.m))
  # Application correction 1 ensemble
  P.for_ensemble_mat[P.for_ensemble_mat < as.numeric(P.thr_ensemble)] = 0
  # Multplier factor for forecasting correction 2
  P.m_ensemble <- 
  sum(P.hist_mat, na.rm = TRUE) / (
    sum(P.for_ensemble_mat, na.rm = TRUE) / (dim(P.db[[1]][[2]])[2]-1))
  flog.info(paste0("Evaluated P.m_ensemble: ", P.m_ensemble))
  if (P.m_ensemble > 1.25) {
    P.m_ensemble <- 1.25
  }
  if (P.m_ensemble < 0.75) {
    P.m_ensemble <- 0.75
  }
  flog.info(paste0("Used P.m_ensemble to apply bias: ", P.m_ensemble))
  # 
  if (length(new_data) != 0) {
    # Bias correction
    for (i in (P.length_orig+1):length(P.db)) {
      # Mean forecasting correction
      datetime <- P.db[[i]][[7]][,1]
      values <- P.for_mean_mat[, i] * P.m
      P.db[[i]][[8]] <- cbind.data.frame(datetime,values)
      # ensemble forecasting correction
      values <- P.for_ensemble_mat[, i,] * P.m_ensemble
      P.db[[i]][[9]] <- cbind.data.frame(datetime,values)
    }
  }
}
rm(P.hist_mat,P.for_mean_mat,P.bias_mean_mat,
  P.for_ensemble_mat,P.W_for,P.W_his,P.W_for_ensemble,
  P.bias_ensemble_mat,j)


###################################################################################
## PROCESS ON REQUESTED DATE
###################################################################################

new_all_date_P <- vector()
## collect names of all RData dates [old + new]
for (j in 1:length(P.db)) {
  new_all_date_P[j] <- P.db[[j]][[1]][[3]]
}

new_all_date_T <- vector()
## collect names of all RData dates [old + new]
for (j in 1:length(T.db)) {
  new_all_date_T[j] <- T.db[[j]][[1]][[3]]
}

## check if requested date is in the new data
has_for_T.data <- is.element(paste0(opt$date, ".csv"), T.for_new_data)
## check if requested date is in the new data
has_for_P.data <- is.element(paste0(opt$date, ".csv"), P.for_new_data)

#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#
#    Case 1: Already calculated bias corrected weather forecast data       #
#            for the required release and date                             #
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------#

## the date requested is not a new data >> check if it is in the RData
if ((is.element(paste0(opt$date, ".csv"), new_all_date_P)) && 
    (is.element(paste0(opt$date, ".csv"), new_all_date_T))) {

  flog.info(paste(
    "Weather forecast data already calculated for the date:", opt$date))

  flog.info("Writing output: unbiased forecast data")

  #------------------------ TEMPERATURE --------------------------#
  idx <- which(new_all_date_T == paste0(opt$date,".csv"))

  T.output_mean_df <- T.db[[idx]][[8]]
  T.output_ens_df <- T.db[[idx]][[9]]

  #------------------------ PRECIPITATION ------------------------#
  idx <- which(new_all_date_P == paste0(opt$date,".csv"))

  P.output_mean_df <- P.db[[idx]][[8]]
  P.output_ens_df <- P.db[[idx]][[9]]
#
} else {

  #--------------------------------------------------------------------------#
  #--------------------------------------------------------------------------#
  #    Case 2: Calculation of the bias corrected weather forecast data       #
  #            for the required release and date,                            #
  #            not in T.db and P.db because something is not complete.       #
  #--------------------------------------------------------------------------#
  #--------------------------------------------------------------------------#
  if ((has_for_P.data == TRUE) && (has_for_T.data == TRUE)) {

    #--------------------------------------------------------------------#
    #                  Correction of the requested data                  #
    #--------------------------------------------------------------------#


    flog.info(paste0("Application of bias correction on: ", opt$date))

    ## TEMPERATURE
    ## read input forecast
    c_for_temp <- 
      as.data.frame(
        read_delim(paste0(path_temp_forc, opt$date, ".csv"), ",",
        escape_double = FALSE,
        col_types = cols(
            datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
        )
      )

    if (any(is.na(c_for_temp))) {
      flog.warn(paste0("Incomplete temperature forecasting data: ", opt$date))
      stop("No data..stopping.")
    }

    ## ensemble bias [4] >> not evaluable
    ## ensemble bias mean [5] >> not evaluable
    ## ensemble bias variance [6] >> not evaluable
    ## mean of the ensemble [7]
    datetime <- c_for_temp[,1]
    values <- rowMeans(c_for_temp[,-1])

    ## unbiased mean [8]
    unbiased_values_mean <- values - bc
    T.output_mean_df <- cbind.data.frame(
      datetime,
      values=unbiased_values_mean
    )

    ## unbiased ensemble [9]
    unbiased_values_ens <- c_for_temp[,-1] - bc
    T.output_ens_df <- cbind.data.frame(
      datetime,
      values=unbiased_values_ens
    )

    ## PRECIPITATION
    ## read input forecast
    c_for_prec <- 
      as.data.frame(
        read_delim(paste0(path_prec_forc, opt$date, ".csv"), ",",
        escape_double = FALSE,
        col_types = cols(
            datetime = col_datetime(format = "%Y-%m-%d %H:%M:%S"))
        )
      )

    if (any(is.na(c_for_prec))) {
      flog.warn(paste0("Incomplete precipitation forecasting data: ", opt$date))
      stop("No data..stopping.")
    }

    ## ensemble bias [4] >> not evaluable
    ## ensemble bias mean [5] >> not evaluable
    ## ensemble bias variance [6] >> not evaluable
    ## mean of the ensemble [7]
    datetime <- c_for_prec[,1]
    values <- rowMeans(c_for_prec[,-1])

    ## unbiased mean [8]
    values[values < as.numeric(P.thr)] = 0
    unbiased_values_mean <- (values * P.m)
    P.output_mean_df <- cbind.data.frame(
      datetime,
      values = unbiased_values_mean)

    ## unbiased ensemble [9]
    c_for_prec[,-1][c_for_prec[,-1] < as.numeric(P.thr_ensemble)] = 0
    unbiased_values_ens <- c_for_prec[,-1] * P.m_ensemble
    P.output_ens_df <- cbind.data.frame(
      datetime,
      values = unbiased_values_ens
    )
  } ## check which are the missed data of the requested date
  else {
    if ((has_for_P.data != TRUE) || (has_for_T.data != TRUE)) {
      flog.warn(paste(
        "No forecast input data available for the date:",
        opt$date)
      )
      if (has_for_P.data != TRUE) {
        flog.warn(paste(
          "Missing precipitation ICON data for the date:",
          opt$date)
        )
      }
      if (has_for_T.data != TRUE) {
        flog.warn(paste(
          "Missing temperature ICON data for the date:",
          opt$date)
        )
      }
      stop("No data..stopping.")
    }
  }
}
#--------------------------------------------------------------------#
#                             Outputs                                #
#--------------------------------------------------------------------#
#
flog.info("Writing outputs")
#
#------------------------ TEMPERATURE -------------------------------#
tmp_dir_mean <- paste0(
  opt$output, md$paths$output_path, opt$basin, "/", opt$subbasin, "/",
  md$initialisation, "/temperature/mean")
tmp_dir_ensemble <- paste0(
  opt$output, md$paths$output_path, opt$basin, "/", opt$subbasin, "/",
  md$initialisation, "/temperature/ensemble")
#
if (!file.exists(tmp_dir_mean)){
  dir.create(file.path(tmp_dir_mean), recursive = TRUE)
}
if (!file.exists(tmp_dir_ensemble)){
  dir.create(file.path(tmp_dir_ensemble), recursive = TRUE)
}

## mean
write_results(
  T.output_mean_df[,1],
  round(T.output_mean_df[,2], digits = 2),
  c("datetime","values"),
  paste0(tmp_dir_mean, "/", opt$date, ".csv")
)

## ensemble
write_results(
  T.output_ens_df[,1],
  c(as.list(
    round(T.output_ens_df[,2:length(T.output_ens_df)],
    digits = 2))),
  c("datetime","1","2","3","4","5","6","7","8","9","10",
  "11","12","13","14","15","16","17","18","19","20"),
  paste0(tmp_dir_ensemble, "/", opt$date, ".csv")
)

#------------------------ PRECIPITATION -----------------------------#
tmp_dir_mean <- paste0(
  opt$output, md$paths$output_path, opt$basin, "/", opt$subbasin, "/",
  md$initialisation, "/precipitation/mean")
tmp_dir_ensemble <- paste0(
  opt$output, md$paths$output_path, opt$basin, "/", opt$subbasin, "/",
  md$initialisation, "/precipitation/ensemble")

#
if (!file.exists(tmp_dir_mean)){
  dir.create(file.path(tmp_dir_mean), recursive = TRUE)
}
if (!file.exists(tmp_dir_ensemble)){
  dir.create(file.path(tmp_dir_ensemble), recursive = TRUE)
}

## mean
write_results(
  P.output_mean_df[,1],
  round(P.output_mean_df[,2], digits = 2),
  c("datetime","values"),
  paste0(tmp_dir_mean, "/", opt$date, ".csv")
)

## ensemble
write_results(
  P.output_ens_df[,1],
  c(as.list(
    round(P.output_ens_df[,2:length(P.output_ens_df)],
    digits = 2))),
  c("datetime","1","2","3","4","5","6","7","8","9","10",
  "11","12","13","14","15","16","17","18","19","20"),
  paste0(tmp_dir_ensemble, "/", opt$date, ".csv")
)

# SetUp Rdata updating
tmp_dir <- paste0(
  opt$output, md$paths$output_path, opt$basin, "/", opt$subbasin, "/",
  md$initialisation, "/SetUp")
if (!file.exists(tmp_dir)){
  dir.create(file.path(tmp_dir), recursive = TRUE)
}

# Save results
assign(paste0("T.", opt$subbasin),T.db)
rm(T.db)
# Save results
assign(paste0("P.", opt$subbasin),P.db)
rm(P.db)
#
# saving
save(list = c(paste0("T.", opt$subbasin), paste0("P.", opt$subbasin)),
      file = paste0(tmp_dir, "/","SetUp.RData"))

#--------------------------------------------------------------------#

#--------------------------------------------------------------------#
#                          Metrics                                   #
#--------------------------------------------------------------------#

#-------------------------- TEMPERATURE -----------------------------#

flog.debug(paste("Metrics calculation"))
# dataframe
T.df <- eval(parse(text = paste0("T.", opt$subbasin))) 
#
VAR <- data.frame(matrix(
  NA, nrow = 4, ncol = length(T.df)),check.names = FALSE)
MAE <- data.frame(matrix(
  NA, nrow = 3, ncol = length(T.df)),check.names = FALSE)
rownames(MAE)<-c("Forecast","Unba_mean","Unba_ense")
rownames(VAR)<-c("Meter","Forecast","Unba_mean","Unba_ense")
#
for (i in 1:length(T.df)) {
  # ensemble
  mae_ens <- vector(length = dim(T.df[[1]][[2]])[2]-1)
  var_ens <- vector(length = dim(T.df[[1]][[2]])[2]-1)
  for (j in 1:(dim(T.df[[1]][[2]])[2]-1)) {
    tryCatch({
      mae_ens[j] <- (mae(T.df[[i]][[3]][,2],T.df[[i]][[9]][,1+j]))},
      error = function(e){}
    )
    tryCatch({
      var_ens[j] <- (var(T.df[[i]][[9]][,1+j]))},
      error = function(e){}
    )
  }
  #
  if ((length(mae_ens[mae_ens == FALSE]) == dim(T.df[[1]][[2]])[2]-1) &&
    (class(mae_ens) == "logical")) {
    mae_mean_ens <- NA
    var_mean_ens <- NA
    mae_mean <- NA
    var_mean <- NA
  }else{
    mae_mean_ens <- try(mean(mae_ens))
    var_mean_ens <- try(mean(var_ens))
    #
    mae_mean <- mae(T.df[[i]][[3]][,2],T.df[[i]][[8]][,2])
    var_mean <- var(T.df[[i]][[8]][,2])
  }
  #
  MAE[, i] <- try(c(mae(T.df[[i]][[3]][,2],T.df[[i]][[7]][,2]),
                    mae_mean,
                    mae_mean_ens))
  #
  VAR[, i] <-  try(c(var(T.df[[i]][[3]][,2]),
                    var(T.df[[i]][[7]][,2]),
                    var_mean,
                    var_mean_ens))
}
#
M_MAE <- rowMeans(MAE, na.rm = TRUE) 
M_VAR <- rowMeans(VAR, na.rm = TRUE)

T.metrics <- list(MAE = MAE, VAR = VAR, M_MAE = M_MAE, M_VAR = M_VAR)
# Save results
assign(paste0("T.metrics_", opt$subbasin),T.metrics)
rm(T.metrics, MAE,VAR,var_mean,var_mean_ens,
  mae_mean, mae_ens, mae_mean_ens)

#-------------------------- PRECIPITATION ---------------------------#

# dataframe
P.df <- eval(parse(text = paste0("P.", opt$subbasin)))
#
MAE <- data.frame(matrix(
  NA, nrow = 3, ncol = length(P.df)),check.names = FALSE)
VAR <- data.frame(matrix(
  NA, nrow = 4, ncol = length(P.df)),check.names = FALSE)
WET <- data.frame(matrix(
  NA, nrow = 4, ncol = length(P.df)),check.names = FALSE)
BAL <- data.frame(matrix(
  NA, nrow = 4, ncol = length(P.df)),check.names = FALSE)
#
rownames(MAE)<-c("Forecast","Unba_mean","Unba_ense")
rownames(VAR)<-c("Meter","Forecast","Unba_mean","Unba_ense")
rownames(WET)<-c("Meter","Forecast","Unba_mean","Unba_ense")
rownames(BAL)<-c("Meter","Forecast","Unba_mean","Unba_ense")
#
for (i in 1:length(P.df)) {
  # ensemble
  mae_ens <- vector(length = dim(P.df[[1]][[2]])[2]-1)
  var_ens <- vector(length = dim(P.df[[1]][[2]])[2]-1)
  wet_ens <- vector(length = dim(P.df[[1]][[2]])[2]-1)
  bal_ens <- vector(length = dim(P.df[[1]][[2]])[2]-1)
  #
  for (j in 1:(dim(P.df[[1]][[2]])[2]-1)) {
    tryCatch({
      mae_ens[j] <- (mae(P.df[[i]][[3]][,2],P.df[[i]][[9]][,1+j]))},
      error = function(e){})
    tryCatch({
      var_ens[j] <- (var(P.df[[i]][[9]][,1+j]))},
      error = function(e){})
    tryCatch({
      wet_ens[j] <- sum((P.df[[i]][[9]][,1+j])!= 0, na.rm = TRUE) },
      error = function(e){})
    tryCatch({
      bal_ens[j] <- sum((P.df[[i]][[9]][,1+j]), na.rm = TRUE) },
      error = function(e){})
  }
  #
  if ((length(mae_ens[mae_ens == FALSE]) == dim(P.df[[1]][[2]])[2]-1) &&
    (class(mae_ens) == "logical")) {
    mae_mean_ens <- NA
    var_mean_ens <- NA
    wet_mean_ens <- NA
    bal_mean_ens <- NA
    mae_mean <- NA
    var_mean <- NA
    wet_mean <- NA
    bal_mean <- NA
  }else{
    mae_mean_ens <- try(mean(mae_ens, na.rm = TRUE))
    var_mean_ens <- try(mean(var_ens, na.rm = TRUE))
    wet_mean_ens <- try(mean(wet_ens, na.rm = TRUE))
    bal_mean_ens <- try(mean(bal_ens, na.rm = TRUE))
    #
    mae_mean <- mae(P.df[[i]][[3]][,2],P.df[[i]][[8]][,2])
    var_mean <- var(P.df[[i]][[8]][,2])
    wet_mean <- sum((P.df[[i]][[8]][,2])!= 0, na.rm = TRUE)
    wet_hist <- sum((P.df[[i]][[3]][,2])!= 0, na.rm = TRUE)
    wet_for <- sum((P.df[[i]][[7]][,2])!= 0, na.rm = TRUE)
    bal_mean <- sum(P.df[[i]][[8]][,2])
  }
  #
  MAE[, i] <- try(c(mae(P.df[[i]][[3]][,2],P.df[[i]][[7]][,2]),
                    mae_mean,
                    mae_mean_ens))
  
  VAR[, i] <-  try(c(var(P.df[[i]][[3]][,2]),
                    var(P.df[[i]][[7]][,2]),
                    var_mean,
                    var_mean_ens))
  
  WET[, i] <-  try(c(wet_hist,
                    wet_for,
                    wet_mean,
                    wet_mean_ens))
  
  BAL[, i] <-  try(c(sum(P.df[[i]][[3]][,2]),
                    sum(P.df[[i]][[7]][,2]),
                    bal_mean,
                    bal_mean_ens))
}      

#
M_MAE <- rowMeans(MAE, na.rm = TRUE) 
M_VAR <- rowMeans(VAR, na.rm = TRUE)
S_WET <- rowSums(WET, na.rm = TRUE)
S_BAL <- rowSums(BAL, na.rm = TRUE)

#
P.metrics <- list(MAE = MAE, VAR = VAR, WET = WET, 
                  M_MAE = M_MAE, M_VAR = M_VAR, 
                  S_WET = S_WET,  S_BAL = S_BAL)
# Save results
assign(paste0("P.metrics_", opt$subbasin),P.metrics)
suppressWarnings(
  rm(P.metrics, mAE,VAR,WET,BAL,var_mean,var_mean_ens, mae_mean, mae_ens,
    mae_mean_ens,wet_mean,wet_mean_ens,wet_hist,wet_ens,var_ens,
    M_MAE, m_VAR,S_WET,S_BAL, i,j,WD, info,datetime,
    bal_ens,bal_mean,bal_mean_ens,wet_for)
)

#--------------------------------------------------------------------#

flog.debug("Saving WS")

# save workspace
tmp_dir <- paste0(
  opt$output, md$paths$output_path, opt$basin, "/", opt$subbasin, "/",
  md$initialisation, "/analysis")

if (!file.exists(tmp_dir)){
  dir.create(file.path(tmp_dir), recursive = TRUE)
}
#

save(list = c(
  paste0("T.metrics_", opt$subbasin), paste0("P.metrics_", opt$subbasin),
  paste0("T.", opt$subbasin), paste0("P.", opt$subbasin)),
  file = paste0(tmp_dir, "/","workspace",".RData"))