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
├── 1. extract_video_frames.ipynb     # Python notebook for extracting .jpeg frames from .mp4 files
├── 2. data_inspection.ipynb          # Python notebook for inspecting object detection labelled images for correct formatting prior to model training
├── 3. model_training.ipynb           # Python notebook for training and evaluating YOLO models
├── 4. model_inference                # Python notebook for using trained YOLO model to predict on raw data
├── 5. model_logging                  # Python notebook for logging and registering final model in MLFlow for serving endpoints
├── yolo11n.pt                     # PyTorch ML model file from Ultralytics yolo version 11
└── yolov8n.pt                     # PyTorch ML model file from Ultralytics yolo version 8
```



## Workflow
1. Image extraction 
   - Extraction of .jpeg frames from video images for model training
2. Data labelling
   - Roboflow option
   - AML option
   - Databricks option (coming soon...)
3. Data Preperation
   - Inspect labelled datasets
4. Object detection model training and evaluation
   - YOLOv8 model
   - YOLOv11 model
   - MLFlow
5. Model inference
   - Script to use model to predict fish in new video data
6. Model logging
   - Log and register model in MLFlow
7. Model serving endpoint
   - Generate a model serving endpoint & serve through databricks apps
  

   
## Requirements
- Databricks: Running the scripts requires access to a Unity Catalog enabled workspace
- Python version: Ensure you are using Python 3.6 and above
- Fish videos in Unit Catalog



## Set-up Instructions
### Step 1: Clone the repository 
Follow cloning instructions from the [Dash Playbook](https://dash-connect-prd.azure.defra.cloud/DASH-Playbook/docs/databricks.html#github) to git clone https://github.com/Defra-Data-Science-Centre-of-Excellence/SpottingSalmon.git

### Step 2: Image extraction 
Run image extraction script to extract frames from video files for use in data labelling and model training steps.

### Step 3: Bounding box labelling 
Download extracted images to local PC and then follow either option 1 or option 2. Additional images for data labelling can be found in the repo in the fish_500.zip file. 

##### Option 1 - Roboflow
Use [Roboflow](https://roboflow.com/annotate) to generate bounding box labels around fish. It is recommended that you augment the data brightness (+/- 25%) and exposure (+/- 10%) to bolster dataset. Extract in YOLOv8 annotation format. Upload the files to Databricks File System (DBFS) using the Create > upload button and move to an appropriate directory (dbutils.fs.cp("local/path/to/labels", "dbfs:/mnt/lab/unrestricted/rachel/labels").

##### Option 2 - AML
Ingest image frames to AML datastore (contact datascience@defra.gov.uk. for assistance) and create as a data asset. Use AML datalabelling tool to generate bounding box labels around fish (note this can be done as a coordinated task with an ML assist option - see [AML labeling project](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-image-labeling-projects?view=azureml-api-2) for guidance). Once labelled, either a) export labels to your local PC and then upload the files to Databricks File System (DBFS) using the Create > upload button and move to an appropriate directory (dbutils.fs.cp("local/path/to/labels", "dbfs:/mnt/lab/unrestricted/rachel/labels"), or b) find the path to your labelled files for direct access via Databricks. 

!Note! There is an option to continue a full workflow on AML by exporting labels as a data asset and using Auto ML to generate an object detection model and executing an endpoint, though previous experience with ML models and evaluation is advised here. Contact rachel.lennon@defra.gov.uk for more details. 

##### Option 3 - Databricks
The Databricks team has made an app that can be used on databricks to label images and save directly to the lakehouse or Unity Catalog. This is currently in development but aims to be available soon for end-to-end workflow in databricks. 

### Step 4: Train model
Open the model_training notebook and run the script to train and evaluate YOLOv8 and YOLOv11 models. 

### Step 5: Use models to predict fish
Open the model_inference notebook to use trained model to generate fish counts from unseen videos.

### Step 6: Model Endpoint
Open the model_logging notebook to log and register the model in the workspace, then using the UI to serve the model. 

### Step 7: App development and deployment 
Use databricks apps and streamlit to make your very own app!

