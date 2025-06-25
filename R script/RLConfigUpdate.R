## CONFIGURATION ----
# Run loop of csv files through rmd with configuration parameters applied 
# Scripts calls to the testdoc3Feb21.rmd file 
# Will call for configuration parameters including:
# Threshold, type of detection, pre-scaling of water baird data etc.

## Set up ----
# Packages
library(utils)
library(data.table)


# Set working directory - editable
setwd("~/SpottingSalmon")

## Get data ----
# Set specific directory for files. 
csv_dir <- "/dbfs/mnt/lab/unrestricted/rachel.lennon@defra.gov.uk/extracted_csv"

# Create a list of the files based on the path
files <- list.files(path = csv_dir, full.names = TRUE)

## Apply .rmd ----
# Loop through .rmd file inputting each .csv in files list 1 by 1. 
for(files_selected in files){
  
  # Generate path to file directory. 
  sel_dirname <- dirname(files_selected)
  
  # Generate word document with same name as file. 
  sel_ofname <- gsub(" ", "", sub("\\.csv\\.gz$", "", basename(files_selected)))
  sel_ofname <- paste0(sel_ofname, ".docx")
  

  # invert electrodes for east stoke [true] but not KM
  
  rmarkdown::render(
    input = '~/SpottingSalmon/testdoc3Feb21.rmd',
    quiet = TRUE,
    output_file = file.path(sel_dirname , sel_ofname)
    , params = list(
      directory = sel_dirname
      , file      = sel_filename
      , THR = 30     #30-BP for KMTH 35 for ES-UniP 40 for gaters Gun 30 Rest1 20
      , bpfind = T
      , writetocsv = T
      , invertelectrodes = F #KM=F ES=T GAT=F KMGW logie=F
      , prescalefactor = 1
      # NB set hpf to 1 for logie only and set prescale divisor
      # Gaters 30 BP non inverted prescale divisor factor 800 - now optimum is 400 (dec 3 2022) with 15 threshold
      # KMTH 30 BP non-inverted prescale divisor 1
      # KMGW ch17-20 20 BP non inverted prescale 200 (prescale in doc comes out as 100)
      # Gun 30 BP non-inverted prescale divisor factor 200
      # East stoke 30 BP non-inverted prescale divisor 1 NB params prescalefactor is ignored for GS1
      # Rest1 20 BP non-inverted prescale divisor factor 200
    )
  )
  print(event_count)
}

#round(length(Diff)/1440,0)
#spm<-floor(sps*60)
#salen<-floor(length(Diff)/spm)*spm
#matrix(Diff[1:salen],ncol=spm,byrow=TRUE)

