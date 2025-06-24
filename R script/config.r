
#------------------------------
# This file is just to facillitate being able to select multiple ghrec csv files and apply a few config parameters for the run like
# thrshold, type of detection, any pre-scaling of water baird data etc.
# the main work gets done in the testdoc3Feb21.rmd file
#-------------------------------



#infile = "p:\\KM 2022\\km-04-2022\\test-KMThu16-2022-04-03-10-19-35Z.csv.gz"

#files_selected <- 'p:\\KM 2022\\km-04-2022\\test-KMThu16-2022-04-11-10-19-43Z.csv.gz'


#with_dir("p:\\KM 2022\\km-01-2022")
setwd("P:\\gaters")
f <- choose.files(multi=T,default = "*.csv",caption="Select raw data file")

for(files_selected in f){
 

  sel_dirname <- dirname(files_selected)
  sel_filename <- basename(files_selected)
  sel_ofname <- gsub(".csv.gz","",paste(basename(sel_filename),'.docx')) # make outfile name
  sel_ofname <- gsub(" ","",sel_ofname) #remove errant space


  # invert electrodes for east stoke [true] but not KM
  
  rmarkdown::render(
      input = 'C:\\Users\\User1\\Documents\\ghd\\testdoc3Feb21.rmd',
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

