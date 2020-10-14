# This Helps you do labeling with OpenCV Contours
First and formost, you need to have preprocessed image

## Compile with pyinstaller
    pyinstaller -D LabelHelper.py

## How to Use
    python LabelHelper.py [-p] 
    -p      Preview Contours result
    
## Default Setting File
#### **`settings.ini`**
```ini
[GeneralSettings]
imagedir = ../images

[ContoursSettings]
threshold = 20
colormax = 255
mode = 1
```

    
    
