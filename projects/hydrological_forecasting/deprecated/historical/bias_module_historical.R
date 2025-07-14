#------------------------------------------------------------------------------#
#                                                                              #
#         Title: Bias correction module                                        #
#         Project: Hydrological AI forecasting chain                           #
#         Aim: Correction weather forecasting for different basins             #
#         Mode: Historical                                                     #
#         Version: 1.0.0                                                       #
#         Author: Andrea Menapace                                              #
#         Date: 01/2022                                                        #
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
library(optparse)
# Time zone
Sys.setenv(TZ='UTC')
Sys.timezone()

#------------------------------------------------------------------------------#
#                                JSON config                                   #
#------------------------------------------------------------------------------#

# option_list = list(
#   make_option(
#     c("-w", "--wdir"), type="character", 
#     default="/home/rstudio/src/", 
#     help="wdir", metavar="character"),
#   make_option(
#     c("-r", "--release"), type="character", 
#     help="running release", metavar="character"),
#   make_option(
#     c("-b", "--basin"), type="character", 
#     help="basin", metavar="character"),
#   make_option(
#     c("-s", "--subbasin"), type="character", 
#     help="subbasin", metavar="character"),
#   make_option(
#     c("-p", "--parameters"), type="character",
#     default='/home/rstudio/etc/conf/parameters.json',
#     help="parameters file", metavar="character"),
#   make_option(
#     c("-i", "--input"), type="character",
#     default='/home/rstudio/data/input/',
#     help="input path", metavar="character"),
#   make_option(
#     c("-o", "--output"), type="character",
#     default='/home/rstudio/data/output/',
#     help="output path", metavar="character")
# )

# opt_parser = OptionParser(option_list=option_list);
# opt = parse_args(opt_parser);

opt <- {}

opt$wdir <- '/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/bias/historical/'
# opt$date <- '20230405'
opt$release <- 'R003'
opt$basin <- 'B001'
opt$subbasin <- 'SB001'
opt$parameters <- '/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/historical/parameters.json'
opt$input <- "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/data/bias/inputs/"
opt$output <- "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/data/bias/outputs/"

setwd(opt$wdir)

#------------------------------------------------------------------------------#
#                                Metadata                                      #
#------------------------------------------------------------------------------#
# Metadata
md <- fromJSON(file=opt$parameters)
N.for <- md$forecasting_horizon

#--------------------------------- Paths --------------------------------------#

# Temperature forecasting data
path_temp_forc <- paste0(opt$input,"icon/postprocessed/",opt$basin,"/",opt$subbasin,"/",opt$release,"/",md$paths$dwd_temperature_path)
# Temperature historical data
path_temp_hist <- paste0(opt$input,"provinz/",opt$basin,"/",opt$subbasin,"/",opt$release,"/",md$paths$aa_temperature_path)
# Precipitation historical data
path_prec_forc <- paste0(opt$input,"icon/postprocessed/",opt$basin,"/",opt$subbasin,"/",opt$release,"/",md$paths$dwd_precipitation_path)
# Precipitation forecasting data
path_prec_hist <- paste0(opt$input,"provinz/",opt$basin,"/",opt$subbasin,"/",opt$release,"/",md$paths$aa_precipitation_path)

# 
paths <- cbind.data.frame(path_temp_hist,path_temp_forc,path_prec_hist,path_prec_forc)
rm(path_temp_hist,path_temp_forc,path_prec_hist,path_prec_forc)

#------------------------------------------------------------------------------#
#                         Main catchments loop                                 #
#------------------------------------------------------------------------------#
  
#----------------------------------------------------------------------------#
#                          Import data                                       #
#----------------------------------------------------------------------------#

for (i in 1:dim(paths)[2]){
  
  names <- c("T_his","T_for","P_his","P_for")
  path_tmp <- paths[[i]][1]
  name_list_tmp = list.files(path = path_tmp,pattern="*.csv")
  tmp_list <- list()
  #
  tmp_date <- name_list_tmp
  
  for (j in 1:length(name_list_tmp)){
    name_tmp <- name_list_tmp[j]
    tmp <- paste(path_tmp,"/",name_tmp,sep="")
    tmp_list[[j]] <- list(name_tmp,as.data.frame(read_delim(tmp, ",", escape_double = FALSE,
                                                            col_types = cols(datetime = col_datetime
                                                                              (format = "%Y-%m-%d %H:%M:%S")),
                                                            trim_ws = TRUE)))
    
    
    # NA and uncompleted
    if(!(length(is.na(tmp_list[[j]][[2]][,2])[is.na(tmp_list[[j]][[2]][,2]) == TRUE])!=0 | 
          length(tmp_list[[j]][[2]][,2])!=N.for)==FALSE){tmp_date[j] = FALSE}
    
  }
  #
  assign(paste0(names[i]),tmp_list)
  assign(paste0(names[i],"_check"),tmp_date)
  rm(tmp_list,tmp_date)
}

# Remove date with empty ICON or historical samples
#
T_for_check_FALSE <- T_for_check[T_for_check!=FALSE]
T_his_check_FALSE <- T_his_check[T_his_check!=FALSE]
P_for_check_FALSE <- P_for_check[P_for_check!=FALSE]
P_his_check_FALSE <- P_his_check[P_his_check!=FALSE]
#
T_date <- T_for_check_FALSE[(T_for_check_FALSE[T_for_check_FALSE!=FALSE] %in% T_his_check_FALSE[T_his_check_FALSE!=FALSE])]
P_date <- P_for_check_FALSE[(P_for_check_FALSE[P_for_check_FALSE!=FALSE] %in% P_his_check_FALSE[P_his_check_FALSE!=FALSE])]
#
T_true_hist_list <-  T_his_check %in% T_date
T_true_for_list <-  T_for_check %in% T_date
P_true_hist_list <-  P_his_check %in% P_date
P_true_for_list <-  P_for_check %in% P_date
# 
T_his[!T_true_hist_list] = NULL
T_for[!T_true_for_list] = NULL
P_his[!P_true_hist_list] = NULL
P_for[!P_true_for_list] = NULL
#
# Temperature
assign(paste0(names[1],"_",opt$subbasin),T_his)
assign(paste0(names[2],"_",opt$subbasin),T_for)
# Precipitation
assign(paste0(names[3],"_",opt$subbasin),P_his)
assign(paste0(names[4],"_",opt$subbasin),P_for)
#
rm(i,j,name_list_tmp,name_tmp,tmp,path_tmp,
    T_for,T_his,P_his,P_for,P_date,T_date,
    P_for_check,P_for_check_FALSE,T_for_check,T_for_check_FALSE,
    P_his_check,P_his_check_FALSE,T_his_check,T_his_check_FALSE,
    P_true_for_list,P_true_hist_list,T_true_for_list,T_true_hist_list)

#----------------------------------------------------------------------------#
#                          Bias evaluation                                   #
#----------------------------------------------------------------------------#

#------------------- TEMPERATURE bias analysis ------------------------------#

# variables
T_bias <- list()
T_for <- eval(parse(text = paste0("T_for_",opt$subbasin))) 
T_his <- eval(parse(text = paste0("T_his_",opt$subbasin))) 
# Check empty data
if (length(T_his)==0|length(T_for)==0) next
# Calculation
info <- c("1 name","2 ensemble forecasting","3 historical data",
          "4 ensemble bias", "5 mean bias","6 ensemble (bias) variance",
          "7 ensemble mean", "8 unbiased mean", "9 unbiased ensemble")
#
for (j in 1:length(T_for)){
  T_bias[[j]] <- list(list(opt$subbasin,info,T_for[[j]][[1]]),
                      as.data.frame(T_for[[j]][2],check.names=FALSE),
                      as.data.frame(T_his[[j]][2],check.names=FALSE))
  
  # ensemble bias (Forecasting-historical data)
  datetime <- T_bias[[j]][[2]][,1]
  T_bias[[j]][[4]] <- cbind.data.frame(datetime,T_bias[[j]][[2]][,-1]-T_bias[[j]][[3]][,2])
  # Mean ensemble bias
  values <- rowMeans(T_bias[[j]][[4]][,-1])
  T_bias[[j]][[5]] <- cbind.data.frame(datetime,values)    
  # ensemble bias variance (ensemble variance)
  values <- rowVars(as.matrix(T_bias[[j]][[4]][,-1]))
  T_bias[[j]][[6]] <- cbind.data.frame(datetime,values)
  # ensemble mean
  values <- rowMeans(T_bias[[j]][[2]][,-1])
  T_bias[[j]][[7]] <-  cbind.data.frame(datetime,values)
  
}
# Save results
assign(paste0("T_",opt$subbasin),T_bias)
rm(j,T_for,T_his,T_bias)
rm(list= paste0("T_for_",opt$subbasin))
rm(list= paste0("T_his_",opt$subbasin))  

#------------------- PRECIPITATION bias analysis ------------------------------#

# variables
P_bias <- list()
P_for <- eval(parse(text = paste0("P_for_",opt$subbasin))) 
P_his <- eval(parse(text = paste0("P_his_",opt$subbasin)))
# Check empty data
if (length(P_his)==0|length(P_for)==0) next
# Calculation
info <- c("1 name","2 ensemble forecasting","3 historical data",
          "4 ensemble bias", "5 mean bias","6 ensemble (bias) variance",
          "7 ensemble mean", "8 unbiased mean", "9 unbiased ensemble")
#
for (j in 1:length(P_for)){
  P_bias[[j]] <- list(list(opt$subbasin,info,P_for[[j]][[1]]),
                      as.data.frame(P_for[[j]][2],check.names=FALSE),
                      as.data.frame(P_his[[j]][2],check.names=FALSE))
  
  # ensemble bias (Forecasting-historical data)
  datetime <- P_bias[[j]][[2]][,1]
  P_bias[[j]][[4]] <- cbind.data.frame(datetime,P_bias[[j]][[2]][,-1]-P_bias[[j]][[3]][,2])
  # Mean ensemble bias
  values <- rowMeans(P_bias[[j]][[4]][,-1])
  P_bias[[j]][[5]] <- cbind.data.frame(datetime,values)    
  # ensemble bias variance (ensemble variance)
  values <- rowVars(as.matrix(P_bias[[j]][[4]][,-1]))
  P_bias[[j]][[6]] <- cbind.data.frame(datetime,values)
  # ensemble mean
  values <- rowMeans(P_bias[[j]][[2]][,-1])
  P_bias[[j]][[7]] <-  cbind.data.frame(datetime,values)
  
}
# Save results
assign(paste0("P_",opt$subbasin),P_bias)
rm(j,P_for,P_his,P_bias,values)
rm(list= paste0("P_for_",opt$subbasin))
rm(list= paste0("P_his_",opt$subbasin))  


#----------------------------------------------------------------------------#
#                          Bias correction                                   #
#----------------------------------------------------------------------------#

#------------------- TEMPERATURE bias correction ----------------------------#

# dataframe
T_df <- eval(parse(text = paste0("T_",opt$subbasin))) 
#
T_bias_mean_mat <- data.frame(matrix(NA,nrow=length(T_df[[1]][[5]][,1]), ncol=length(T_df)),check.names=FALSE)
#
for (i in 1:length(T_df)) {
  T_bias_mean_mat[,i] <- T_df[[i]][[5]][,2]
}
rm(i)

#------------------- TEMPERATURE: RWM ---------------------------------------#
# method rolling window mean on N past days
if(md$T_forecasting_method=="T_RWM"){
  # number of forecasting events considered for the rolling window of bias correction methods
  WD <- md$T_attribute_for_met
  #
  for (i in 1:(length(T_df)-WD)) {
    
    bc <- rowMeans(T_bias_mean_mat[,((i):(WD+i-1))])
    # Mean forecasting correction
    datetime <- T_df[[WD+i]][[7]][,1]
    values <- T_df[[WD+i]][[7]][,2] - bc
    T_df[[WD+i]][[8]] <- cbind.data.frame(datetime,values)
    # ensemble forecasting correction
    values <- T_df[[WD+i]][[2]][,-1] - bc
    T_df[[WD+i]][[9]] <- cbind.data.frame(datetime,values)
    
  }
}
# Save results
assign(paste0("T_",opt$subbasin),T_df)
rm(T_df,T_bias_mean_mat)#T_hist_mat,T_for_mean_mat

#------------------- PRECIPITATION bias correction --------------------------#

# dataframe
P_df <- eval(parse(text = paste0("P_",opt$subbasin))) 
#
P_hist_mat <- data.frame(matrix(NA,nrow=length(P_df[[1]][[3]][,1]), ncol=length(P_df)),check.names=FALSE)
P_for_mean_mat <- data.frame(matrix(NA,nrow=dim(P_df[[1]][[7]])[1], ncol=length(P_df)),check.names=FALSE)
P_bias_mean_mat <- data.frame(matrix(NA,nrow=length(P_df[[1]][[5]][,1]), ncol=length(P_df)),check.names=FALSE)
# dataframe ensemble
P_for_ensemble_mat <- array(NA,c(dim(P_df[[1]][[2]])[1],
                                  length(P_df),
                                  dim(P_df[[1]][[2]])[2]-1))

P_bias_ensemble_mat <- array(NA,c(dim(P_df[[1]][[2]])[1],
                                  length(P_df),
                                  dim(P_df[[1]][[2]])[2]-1))
#
for (i in 1:length(P_df)) {
  P_hist_mat[,i] <- P_df[[i]][[3]][,2]
  P_for_mean_mat[,i] <- P_df[[i]][[7]][,2]
  P_bias_mean_mat[,i] <- P_df[[i]][[5]][,2]
  #
  for (j in 1:((dim(P_df[[2]][[2]])[2]-1))) {
    P_for_ensemble_mat[,i,j] <- P_df[[i]][[2]][,1+j]
    P_bias_ensemble_mat[,i,j] <- P_df[[i]][[4]][,1+j]
  }
}
rm(i)

#------------------- PRECIPITATION: MWHB ------------------------------------#

if(md$P_forecasting_method=="P_MWHB"){
  # Correction factor estimation
  # Wet hours
  P_W_his <- P_hist_mat; P_W_his[P_W_his!=0] <-1; sum(P_W_his)
  P_W_for <-  P_for_mean_mat; P_W_for[P_W_for!=0] <-1; sum(P_W_for)
  # ensemble
  P_W_for_ensemble <- P_for_ensemble_mat; P_W_for_ensemble[P_W_for_ensemble!=0] <-1
  sum(P_W_for_ensemble)/(dim(P_df[[1]][[2]])[2]-1)
  # statistics
  sum(P_W_his); sum(P_hist_mat);(sum(P_W_his)/(dim(P_W_his)[1]*dim(P_W_his)[2]))
  sum(P_W_for); sum(P_for_mean_mat);(sum(P_W_for)/(dim(P_W_for)[1]*dim(P_W_for)[2]))
  # ensemble
  sum(P_W_for_ensemble)/(dim(P_df[[1]][[2]])[2]-1)
  sum(P_for_ensemble_mat)/(dim(P_df[[1]][[2]])[2]-1)
  (sum(P_W_for_ensemble)/(dim(P_W_for_ensemble)[1]*dim(P_W_for_ensemble)[2]*dim(P_W_for_ensemble)[1]))
  # Threshold null precipitation (<) for forecasting correction 1
  P_thr <- quantile(as.numeric(as.matrix(P_for_mean_mat)),
                    1-(sum(P_W_his)/(dim(P_W_his)[1]*dim(P_W_his)[2])))
  # ensemble
  P_thr_ensemble <- quantile(as.numeric(as.matrix(P_for_ensemble_mat)),1-
                                (sum(P_W_his)/(dim(P_W_his)[1]*dim(P_W_his)[2])))
  
  
  
  # Application correction 1 mean
  P_for_mean_mat[P_for_mean_mat < as.numeric(P_thr)] = 0
  # Multplier factor for forecasting correction 2
  P_m <- sum(P_hist_mat)/sum(P_for_mean_mat)
  # Application correction 1 ensemble
  P_for_ensemble_mat[P_for_ensemble_mat < as.numeric(P_thr_ensemble)] = 0
  # Multplier factor for forecasting correction 2
  P_m_ensemble <- sum(P_hist_mat)/(sum(P_for_ensemble_mat)/(dim(P_df[[1]][[2]])[2]-1))
  
  # Bias correction
  for (i in 1:length(P_df)) {
    # Mean forecasting correction
    datetime <- P_df[[i]][[7]][,1]
    values <- P_for_mean_mat[,i] * P_m
    P_df[[i]][[8]] <- cbind.data.frame(datetime,values)
    # ensemble forecasting correction
    values <- P_for_ensemble_mat[,i,] * P_m_ensemble
    P_df[[i]][[9]] <- cbind.data.frame(datetime,values)
    
  }
  
}
# Save results
assign(paste0("P_",opt$subbasin),P_df)
rm(P_df,P_hist_mat,P_for_mean_mat,P_bias_mean_mat,
    P_for_ensemble_mat,P_W_for,P_W_his,values,P_W_for_ensemble)
rm(P_m,P_m_ensemble,P_thr,P_thr_ensemble,P_bias_ensemble_mat,bc)

#----------------------------------------------------------------------------#
#                          Metrics                                           #
#----------------------------------------------------------------------------#

#-------------------------- TEMPERATURE -------------------------------------#

# dataframe
T_df <- eval(parse(text = paste0("T_",opt$subbasin))) 
#
VAR <- data.frame(matrix(NA,nrow = 4,ncol=length(T_df)),check.names=FALSE)
MAE <- data.frame(matrix(NA,nrow = 3,ncol=length(T_df)),check.names=FALSE)
rownames(MAE)<-c("Forecast","Unba_mean","Unba_ense")
rownames(VAR)<-c("Meter","Forecast","Unba_mean","Unba_ense")
#
for (i in 1:length(T_df)) {
  
  # ensemble
  mae_ens <- vector(length = dim(T_df[[1]][[2]])[2]-1)
  var_ens <- vector(length = dim(T_df[[1]][[2]])[2]-1)
  for (j in 1:(dim(T_df[[1]][[2]])[2]-1)) {
    tryCatch({mae_ens[j] <- (mae(T_df[[i]][[3]][,2],T_df[[i]][[9]][,1+j]))}, error=function(e){})
    tryCatch({var_ens[j] <- (var(T_df[[i]][[9]][,1+j]))}, error=function(e){})
  }
  #
  if ((length(mae_ens[mae_ens==FALSE])==dim(T_df[[1]][[2]])[2]-1)&(class(mae_ens)=="logical")) {
    mae_mean_ens <- NA
    var_mean_ens <- NA
    mae_mean <- NA
    var_mean <- NA
  }else{
    mae_mean_ens <- try(mean(mae_ens))
    var_mean_ens <- try(mean(var_ens))
    #
    mae_mean <- mae(T_df[[i]][[3]][,2],T_df[[i]][[8]][,2])
    var_mean <- var(T_df[[i]][[8]][,2])
  }
  
  #
  MAE[,i] <- try(c(mae(T_df[[i]][[3]][,2],T_df[[i]][[7]][,2]),
                    mae_mean,
                    mae_mean_ens))
  
  VAR[,i] <-  try(c(var(T_df[[i]][[3]][,2]),
                    var(T_df[[i]][[7]][,2]),
                    var_mean,
                    var_mean_ens))
}
#
M_MAE <- rowMeans(MAE, na.rm = TRUE) 
M_VAR <- rowMeans(VAR, na.rm = TRUE)

T_metrics <- list(MAE = MAE, VAR = VAR, M_MAE = M_MAE, M_VAR=M_VAR)
# Save results
assign(paste0("T_metrics_",opt$subbasin),T_metrics)
rm(T_metrics,MAE,VAR,var_mean,var_mean_ens,mae_mean,mae_ens,mae_mean_ens,
    M_MAE,M_VAR,var_ens)

#-------------------------- PRECIPITATION -----------------------------------#

# dataframe
P_df <- eval(parse(text = paste0("P_",opt$subbasin)))
#
MAE <- data.frame(matrix(NA,nrow = 3,ncol=length(P_df)),check.names=FALSE)
VAR <- data.frame(matrix(NA,nrow = 4,ncol=length(P_df)),check.names=FALSE)
WET <- data.frame(matrix(NA,nrow = 4,ncol=length(P_df)),check.names=FALSE)
BAL <- data.frame(matrix(NA,nrow = 4,ncol=length(P_df)),check.names=FALSE)
#
rownames(MAE)<-c("Forecast","Unba_mean","Unba_ense")
rownames(VAR)<-c("Meter","Forecast","Unba_mean","Unba_ense")
rownames(WET)<-c("Meter","Forecast","Unba_mean","Unba_ense")
rownames(BAL)<-c("Meter","Forecast","Unba_mean","Unba_ense")
#
for (i in 1:length(P_df)) {
  # ensemble
  mae_ens <- vector(length = dim(P_df[[1]][[2]])[2]-1)
  var_ens <- vector(length = dim(P_df[[1]][[2]])[2]-1)
  wet_ens <- vector(length = dim(P_df[[1]][[2]])[2]-1)
  bal_ens <- vector(length = dim(P_df[[1]][[2]])[2]-1)
  #
  for (j in 1:(dim(P_df[[1]][[2]])[2]-1)) {
    tryCatch({mae_ens[j] <- (mae(P_df[[i]][[3]][,2],P_df[[i]][[9]][,1+j]))}, error=function(e){})
    tryCatch({var_ens[j] <- (var(P_df[[i]][[9]][,1+j]))}, error=function(e){})
    tryCatch({wet_ens[j] <- sum((P_df[[i]][[9]][,1+j])!=0, na.rm = TRUE) }, error=function(e){})
    tryCatch({bal_ens[j] <- sum((P_df[[i]][[9]][,1+j]), na.rm = TRUE) }, error=function(e){})
  }
  #
  if ((length(mae_ens[mae_ens==FALSE])==dim(P_df[[1]][[2]])[2]-1)&(class(mae_ens)=="logical")) {
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
    mae_mean <- mae(P_df[[i]][[3]][,2],P_df[[i]][[8]][,2])
    var_mean <- var(P_df[[i]][[8]][,2])
    wet_mean <- sum((P_df[[i]][[8]][,2])!=0, na.rm = TRUE)
    wet_hist <- sum((P_df[[i]][[3]][,2])!=0, na.rm = TRUE)
    wet_for <- sum((P_df[[i]][[7]][,2])!=0, na.rm = TRUE)
    bal_mean <- sum(P_df[[i]][[8]][,2])
  }
  
  #
  MAE[,i] <- try(c(mae(P_df[[i]][[3]][,2],P_df[[i]][[7]][,2]),
                    mae_mean,
                    mae_mean_ens))
  
  VAR[,i] <-  try(c(var(P_df[[i]][[3]][,2]),
                    var(P_df[[i]][[7]][,2]),
                    var_mean,
                    var_mean_ens))
  
  WET[,i] <-  try(c(wet_hist,
                    wet_for,
                    wet_mean,
                    wet_mean_ens))
  
  BAL[,i] <-  try(c(sum(P_df[[i]][[3]][,2]),
                    sum(P_df[[i]][[7]][,2]),
                    bal_mean,
                    bal_mean_ens))
}      

#
M_MAE <- rowMeans(MAE, na.rm = TRUE) 
M_VAR <- rowMeans(VAR, na.rm = TRUE)
S_WET <- rowSums(WET, na.rm = TRUE)
S_BAL <- rowSums(BAL, na.rm = TRUE)

#
P_metrics <- list(MAE = MAE, VAR = VAR, WET = WET, 
                  M_MAE = M_MAE, M_VAR = M_VAR, 
                  S_WET = S_WET,  S_BAL = S_BAL)
# Save results
assign(paste0("P_metrics_",opt$subbasin),P_metrics)
rm(P_metrics,MAE,VAR,WET,BAL,var_mean,var_mean_ens,mae_mean,mae_ens,
    mae_mean_ens,wet_mean,wet_mean_ens,wet_hist,wet_ens,var_ens,
    M_MAE,M_VAR,S_WET,S_BAL,i,j,WD, names,info,datetime,
    bal_ens,bal_mean,bal_mean_ens,wet_for)


#----------------------------------------------------------------------------#
#                             Outputs                                        #
#----------------------------------------------------------------------------#

#------------------------ TEMPERATURE ---------------------------------------#

tmp_dir_mean <- paste0(opt$output,"/",opt$basin,"/",opt$subbasin,"/",
                        opt$release,"/temperature/mean")
tmp_dir_ensemble <- paste0(opt$output,"/",opt$basin,"/",opt$subbasin,"/",
                            opt$release,"/temperature/ensemble")
#
if (!file.exists(tmp_dir_mean)){dir.create(file.path(tmp_dir_mean), recursive = TRUE)}
if (!file.exists(tmp_dir_ensemble)){dir.create(file.path(tmp_dir_ensemble), recursive = TRUE)}


for (i in 1:length(T_df)) {
  
  # Mean
  tryCatch({T_df[[i]][[8]][,2] <- round(T_df[[i]][[8]][,2],digits = 2)}, error=function(e){})
  
  # mean
  d <- T_df[[i]][[8]]
  d$datetime <- format(d$datetime, "%Y-%m-%d %H:%M:%S")
  tryCatch(
    {
      readr::write_csv(
        d,
        paste0(tmp_dir_mean, "/", T_db[[idx]][[1]][[3]])
      )
    }, error = function(e){})
  
  # ensemble
  tryCatch({T_df[[i]][[9]][,2:dim(T_df[[1]][[2]])[2]] <- 
    round(T_df[[i]][[9]][,2:dim(T_df[[1]][[2]])[2]],digits = 2)}, error=function(e){})

  d <- T_df[[i]][[9]]
  d$datetime <- format(d$datetime, "%Y-%m-%d %H:%M:%S")
  tryCatch(
    {
      readr::write_csv(
        d,
        paste0(tmp_dir_ensemble, "/", T_db[[idx]][[1]][[3]])
      )
    }, error = function(e){})
}

#------------------------ PRECIPITATION -------------------------------------# 
tmp_dir_mean <- paste0(opt$output,"/",opt$basin,"/",opt$subbasin,"/",
                        opt$release,"/precipitation/mean")
tmp_dir_ensemble <- paste0(opt$output,"/",opt$basin,"/",opt$subbasin,"/",
                            opt$release,"/precipitation/ensemble")
tmp_dir <- paste0(opt$output,"/",opt$basin,"/",opt$subbasin,"/",
                  opt$release,"/SetUp")
#
if (!file.exists(tmp_dir_mean)){dir.create(file.path(tmp_dir_mean), recursive = TRUE)}
if (!file.exists(tmp_dir_ensemble)){dir.create(file.path(tmp_dir_ensemble), recursive = TRUE)}
if (!file.exists(tmp_dir)){dir.create(file.path(tmp_dir), recursive = TRUE)}

for (i in 1:length(P_df)) {
  
  # mean
  tryCatch({P_df[[i]][[8]][,2] <- round(P_df[[i]][[8]][,2],digits = 2)}, error=function(e){})
  d <- P_df[[i]][[8]]
  d$datetime <- format(d$datetime, "%Y-%m-%d %H:%M:%S")
  tryCatch(
    {
      readr::write_csv(
        d,
        paste0(tmp_dir_mean, "/", T_db[[idx]][[1]][[3]])
      )
    }, error = function(e){})
  
  # ensemble
  tryCatch({P_df[[i]][[9]][,2:dim(P_df[[1]][[2]])[2]] <- 
    round(P_df[[i]][[9]][,2:dim(P_df[[1]][[2]])[2]],digits = 2)}, error=function(e){})

  d <- P_df[[i]][[9]]
  d$datetime <- format(d$datetime, "%Y-%m-%d %H:%M:%S")
  tryCatch(
    {
      readr::write_csv(
        d,
        paste0(tmp_dir_ensemble, "/", T_db[[idx]][[1]][[3]])
      )
    }, error = function(e){})
  
  tryCatch({write.csv(P_df[[i]][[8]], paste0(tmp_dir_mean,"/",P_df[[i]][[1]][[3]]), 
                      row.names = FALSE, quote=F)}, error=function(e){})
}

save(list = c(paste0("T_",opt$subbasin), paste0("P_",opt$subbasin)),
      file = paste0(tmp_dir,"/", "SetUp.RData"))

#----------------------------------------------------------------------------#

# save workspace
tmp_dir <- paste0(opt$output,"/",opt$basin,"/",opt$subbasin,"/",
                  opt$release,"/analysis")

if (!file.exists(tmp_dir)){
  dir.create(file.path(tmp_dir), recursive = TRUE)
}
#

save(list = c(paste0("T_metrics_",opt$subbasin), paste0("P_metrics_",opt$subbasin),
              paste0("T_",opt$subbasin), paste0("P_",opt$subbasin)),
      file = paste0(tmp_dir,"/","workspace",".RData"))