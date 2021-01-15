# This Helps you do labeling with OpenCV Contours
First and formost, you need to have preprocessed image

## Compile with pyinstaller
    pyinstaller -D LabelHelper.py

## How to Use
    python LabelHelper.py [-p][-v] 
    -v      Preview Contours result
    -p      Prefix
    
    ex. python LabelHelper.py -p "Photogroup 1" -v

    
## Default Setting File
#### **`settings.ini`**
```ini
[ContoursSettings]
threshold = 20
colormax = 255
mode = 1
```

    
    
