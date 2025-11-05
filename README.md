# SpottingSalmon
This repository demonstrate a computer vision machine learning workflow using a salmon dataset from the Environment Agency Knapp Mill monitoring site to train YOLO models for object detection. It covers data preprocessing, model training and evaluation, and model prediction using Databricks.

## Table of Contents
- [Project Overview](#project-overview)
- [File Structure](#file-structure)
- [Workflow](#workflow)
- [Requirements](#requirements)
- [Set-up Instructions](#set-up-instructions)
- [Next Steps](#next-steps)

## Project Overview
The research and development project was initiated to automate the monitoring of wild salmon populations as traditional monitoring methods are time-consuming, and resource intensive. The workflow includes: 
- Data preprocessing and visualisation using the salmon dataset
- Training and evaluating object detection models using Ultralytics



## File Structure
Here is an overview of the most important files in the repository

```bash
SpottingSalmon/Video (Object Detection)
│
├── 0.0_ExtractVideoFrame.ipynb    # Python notebook for extracting .jpeg frames from .mp4 files
├── 1.0_ImagePreProcessing.ipynb   # Python notebook for pre-processing
├── 2.0_YOLO.ipynb                 # Python notebook for training and evaluating YOLO models
├── 2.1_YOLO_predict.ipynb         # Python notebook for using trained YOLO model to predict on raw data
├── yolo11n.pt                     # PyTorch ML model file from Ultralytics yolo version 11
└── yolov8n.pt                     # PyTorch ML model file from Ultralytics yolo version 8
```



## Workflow
1. Data Preperation
   - Extract video file frames as images and store in datalake
   - Inspect images
2. Data labelling
   - Roboflow option
   - AML option
3. Object detection model training and evaluation
   - YOLOv8 model
   - YOLOv11 model
5. Model prediction
   - Script to use model to predict fish in new video data
  

   
## Requirements
- Databricks: Running the scripts requires a Databricks environment with access to the Datalake
- Python version: Ensure you are using Python 3.6 and above
- Fish videos: Make sure you have access to fish images through Datalake



## Set-up Instructions
#### Step 1: Clone the repository 
Follow cloning instructions from the [Dash Playbook](https://dap-prd2-connect.azure.defra.cloud/DASH-Playbook/) to git clone https://github.com/Defra-Data-Science-Centre-of-Excellence/SpottingSalmon.git

#### Step 2: Data preperation
Run data preperation script to extract frames from video files, and inscpect images. 

#### Step 3: Bounding box labelling 
######Option 1 - Roboflow
Download extracted images to local PC and then use [Roboflow](https://roboflow.com/annotate) to generate bounding box labels around fish. It is recommended that you augment the data brightness (+/- 25%) and exposure (+/- 10%) to bolster dataset. Extract in YOLOv8 annotation format. Upload the files to Databricks File System (DBFS) using the Create > upload button and move to an appropriate directory (dbutils.fs.cp("local/path/to/labels", "dbfs:/mnt/lab/unrestricted/rachel/labels").

######Option 2 - AML
Ingest image frames to AML datastore (contact datascience@defra.gov.uk. for assistance) and create as a data asset. Use AML datalabelling tool to generate bounding box labels around fish (note this can be done as a coordinated task with an ML assist option - see [AML labeling project](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-image-labeling-projects?view=azureml-api-2) for guidance). Once labelled, either a) export labels to your local PC and then upload the files to Databricks File System (DBFS) using the Create > upload button and move to an appropriate directory (dbutils.fs.cp("local/path/to/labels", "dbfs:/mnt/lab/unrestricted/rachel/labels"), or b) find the path to your labelled files for direct access via Databricks. 

!Note! There is an option to continue a full workflow on AML by exporting labels as a data asset and using Auto ML to generate an object detection model and executing an endpoint, though previous experience with ML models and evaluation is advised here. Contact rachel.lennon@defra.gov.uk for more details. 

#### Step 4: Run scripts
Train YOLO models: Open the yolo.ipynb notebook and run the YOLO script to train and evaluate YOLOv8 and YOLOv11 models. 
Predict with models: Run the YOLO_predict script to use trained models to predict on raw data. 

# Next Steps 
- Find path to  labelled files for direct access via Databricks.  
- Generate an endpoint for use of final model through a GUI
- Test of data labelling options within Databricks (i.e., LabelBox)
