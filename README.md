# AI-Based Fake Seed Detection — Working Prototype

## What this version does
This is a complete Flask web prototype:
- Upload a seed image
- Analyze the image
- Show a "Likely Genuine" / "Likely Fake" result
- Show confidence and image-quality statistics
- Store scan history in SQLite
- View previously analyzed images

## Important
The current `analyze_seed()` function is a DEMO image-statistics classifier.
It is not a scientifically validated seed-authenticity model.

For the final academic project, replace it with a trained CNN/transfer-learning
model trained on genuine and fake/adulterated seed images.

## Requirements
Python 3.14 is installed on your computer.

## Windows setup
Open Command Prompt inside this project folder:

```text
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Then open:
http://127.0.0.1:5000

## Project structure

fake_seed_detection/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   ├── result.html
│   └── history.html
├── static/
│   ├── css/style.css
│   └── js/app.js
├── uploads/
└── data/

## Final-year upgrade
Recommended next stage:
1. Collect genuine/fake seed images.
2. Organize them into train/validation/test folders.
3. Train MobileNetV2/EfficientNet or another suitable CNN.
4. Save the trained model.
5. Replace `analyze_seed()` with model inference.
6. Add seed-type classification and explainable visual features.
7. Evaluate accuracy, precision, recall, F1-score and confusion matrix.
