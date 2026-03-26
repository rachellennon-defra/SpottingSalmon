# Using Computer Vision Approaches to Automate Wild Salmon Monitoring
This repository demonstrate a computer vision machine learning workflow using a salmon dataset from the Environment Agency (EA) monitoring site to train YOLO models for object detection. It covers data preprocessing, model training and evaluation, and front-end development and app deployment using Databricks.

<img width="654" height="395" alt="fish detection 0 91" src="https://github.com/user-attachments/assets/786a1bdd-0678-4e97-a621-8cf55ebe7862" />

## Table of Contents
- [Project Overview](#project-overview)
- [File Structure](#file-structure)
- [Workflow](#workflow)
- [Requirements](#requirements)
- [Set-up Instructions](#set-up-instructions)
- [Acknowledgements and contact details](#acknowledgements-and-contact-details)

## Project Overview
The research and development project was initiated to automate the monitoring of wild salmon populations as traditional monitoring methods are time-consuming, and resource intensive. The workflow includes: 
- Data preprocessing and visualisation using the salmon dataset
- Training and evaluating object detection models using Ultralytics in Databricks
- Logging and registering model using ML flow in Databricks
- Generating a streamlit app in Databricks using Databricks Apps



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
├── dummy_data.zip                    # File containing images of fish passing events priovided by the Environment Agency for data labelling
├── yolo11n.pt                        # PyTorch ML model file from Ultralytics yolo version 11
├── yolov8n.pt                        # PyTorch ML model file from Ultralytics yolo version 8
│
└── app/                          
    ├── app.py                        # Python file for steamlit app backend
    ├── app.yaml                      # YAML file for app set up via databricks apps
    └── requirements.txt              # Text file for package requirements for databricks app

```
Note: Dummy data is provided for training demonstrations only and is not open data.
Dummy data has been provided by the Environment Agency, taken as still images from salmon monitoring videos recorded at EA monitoring site in July 2021. Images display an over-head view of monitoring channel, small passages that salmon pass through when migrating through a river. These images can be used to generate training data for computer vision models. 

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
   - Generate a model serving endpoint using endpoint GUI
8. Generate and deploy Databricks App
   - Use app script to generate a streamlit app and deploy through Databricks app GUI
  

   
## Requirements
- Databricks: Running the scripts requires access to a Unity Catalog enabled workspace
- Python version: Ensure you are using Python 3.6 and above
- Fish images from dummy data

### Data
This workflow assumes you have access to a zip files of fish video monitoring files in an .mp4 format. If you do not have access to this then you can use the dummy_data which contains pre-extracted images in the format .jpeg, and start from script 2 (i.e., ignoring Image Extraction step). 

## Set-up Instructions
### Step 1: Clone the repository 
Follow cloning instructions from the [Dash Playbook](https://dash-connect-prd.azure.defra.cloud/DASH-Playbook/docs/databricks.html#github) to git clone https://github.com/Defra-Data-Science-Centre-of-Excellence/SpottingSalmon.git


### Step 2: Image extraction 
Run image extraction script to extract frames from video files or use dummy_data images for use in data labelling and model training steps.

### Step 3: Bounding box labelling 
Download extracted images to local PC and then follow an option for labelling.

##### Option 1 - Roboflow
Use [Roboflow](https://roboflow.com/annotate) to generate bounding box labels around fish. It is recommended that you augment the data brightness (+/- 25%) and exposure (+/- 10%) to bolster dataset. Extract in YOLOv8 annotation format. Upload the files to Databricks File System (DBFS) using the Create > upload button and move to an appropriate directory.

##### Option 2 - AML
Ingest image frames to AML datastore (contact datascience@defra.gov.uk. for assistance) and create as a data asset. Use AML datalabelling tool to generate bounding box labels around fish (note this can be done as a coordinated task with an ML assist option - see [AML labeling project](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-image-labeling-projects?view=azureml-api-2) for guidance). Once labelled, either a) export labels to your local PC and then upload the files to Databricks File System (DBFS) using the Create > upload button and move to an appropriate directory, or b) find the path to your labelled files for direct access via Databricks. 

!Note! There is an option to continue a full workflow on AML by exporting labels as a data asset and using Auto ML to generate an object detection model and executing an endpoint, though previous experience with ML models and evaluation is advised here. 

##### Option 3 - Databricks
The Databricks team has made an app that can be used on databricks to label images and save directly to the lakehouse or Unity Catalog. This is currently in development but aims to be available soon for end-to-end workflow in databricks. 

### Step 4: Train model
Open the model_training notebook and run the script to train and evaluate YOLOv8 and YOLOv11 models. 

### Step 5: Use models to predict fish
Open the model_inference notebook to use trained model to generate fish counts from unseen videos.

### Step 6: Model Endpoint
Open the model_logging notebook to log and register the model in the workspace, then use the databricks GUI to serve the model (https://docs.databricks.com/aws/en/machine-learning/model-serving/create-manage-serving-endpoints) 

### Step 7: App development and deployment 
Use the Databricks App GUI and the app.py, app.yaml and requirements.txt in /app folder to deploy your own streamlit app using the model endpoint (https://www.databricks.com/product/databricks-apps)


## Acknowledgements and contact details
Data is provided by and the project is owned by the Environment Agency. All data science and code conducted by Department for Environment, Food and Rural Affairs Data Analytics and Science Hub team.

### Contacts
- General technical: DASH data science team - datascience@mailshot.defra.gov.uk
- Project owner & developer: Rachel Lennon (DASH) - rachelllennon@hotmail.com
- AI Technical: Isaac Arhinful (DASH) - Isaac.Arhinful@defra.gov.uk
- Future developments: Margarita Tsakiridou (DASH) - margarita.tsakiridou@defra.gov.uk
- Application and use: Adrian Fewings (Environment Agency) - adrian.fewings@environment-agency.gov.uk

![dash_wide_logo](https://github.com/user-attachments/assets/4ea7b5ee-b8e7-4be1-aded-c1760abbe6ba)
<img width="500" height="261" alt="Department_for_Environment,_Food_and_Rural_Affairs_logo svg" src="https://github.com/user-attachments/assets/a8ee14d5-c582-4e10-98e6-cc00e9125518" />
![EA-logo](https://github.com/user-attachments/assets/4c24c169-68cb-4205-82b3-a8726f61b58c)

