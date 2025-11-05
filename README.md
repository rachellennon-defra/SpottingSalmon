# SpottingSalmon
This repository demonstrate a computer vision machine learning workflow using a salmon dataset from the Environment Agency Knapp Mill monitoring site. It covers data preprocessing, model training and evaluation using Databricks.

## Table of Contents
- [Project Overview](#project-overview)
- [File Structure](#file-structure)


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
### Step 1: Clone the repository 
