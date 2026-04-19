# Student Burnout Detection System

A complete machine learning application with ML backend, Tkinter GUI frontend, and MongoDB integration for detecting and tracking student burnout.

## Project Structure

```
burnout_app/
├── gui/                      # Tkinter GUI components
│   ├── __init__.py
│   ├── student_form.py       # Form input tab
│   ├── results_tab.py        # Prediction results display
│   └── trend_tab.py          # MongoDB trend visualization
│
├── models/                   # ML model files
│   ├── __init__.py
│   ├── preprocess.py         # Data preprocessing & split
│   ├── train_models.py       # Train 4 models + save metrics
│   ├── predictor.py          # Main prediction pipeline
│   ├── shap_analysis.py      # SHAP explainability plots
│   └── *.pkl                 # Saved models and scalers
│
├── db/                       # Database handlers
│   ├── __init__.py
│   └── mongo_handler.py      # MongoDB operations
│
├── data/                     # Data files
│   ├── eda.py               # Exploratory data analysis
│   ├── eda_visualizations.py # Generate EDA plots
│   ├── raw_burnout.csv      # Raw dataset (add manually)
│   ├── clean_burnout.csv    # Cleaned dataset
│   └── *.npy                # Preprocessed arrays
│
├── visuals/                  # Generated visualizations
│   └── *.png                # Plots and charts
│
├── main.py                   # Entry point - starts GUI
├── test_predictor.py         # Test ML predictions
├── test_mongo.py             # Test MongoDB connection
└── requirements.txt          # Python dependencies
```

## Phase 1: ML Backend Setup (Days 1-4)

### Step 1.1: Environment Setup
```bash
cd burnout_app
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Step 1.2-1.3: Data Preparation
1. Download a student burnout dataset from Kaggle
2. Save it as `data/raw_burnout.csv`
3. Run data cleaning:
```bash
python data/eda.py
python data/eda_visualizations.py
```

### Step 1.4-1.5: Train Models
```bash
# Preprocess and split data
python models/preprocess.py

# Train all 4 models and save
python models/train_models.py

# Generate SHAP explanations
python models/shap_analysis.py

# Test predictions
python test_predictor.py
```

**Phase 1 Complete when:**
- ✅ `test_predictor.py` runs without errors
- ✅ Two test cases show different risk labels
- ✅ `visuals/shap_live.png` is created

---

## Phase 2: Tkinter GUI (Days 5-7)

### Files Involved:
- `gui/student_form.py` - Input form with sliders, text field, and submit button
- `gui/results_tab.py` - Displays scores, risk level, and SHAP waterfall
- `main.py` - Wires everything together

### Launch GUI:
```bash
python main.py
```

**Features:**
- Student ID input
- Sleep/Study hours sliders (0-14)
- Anxiety level slider (1-10)
- Social hours slider (0-8)
- Department dropdown
- Mood journal text area
- Sentiment analysis (VADER)
- Real-time SHAP explanations

**Phase 2 Complete when:**
- ✅ Form → Submit → Results tab shows all predictions
- ✅ SHAP waterfall image displays correctly
- ✅ Confidence score and risk color are displayed

---

## Phase 3: MongoDB Integration (Day 8)

### Setup MongoDB:

**Mac (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo systemctl start mongod
```

**Windows:** MongoDB runs as a service automatically after installation

### Files Involved:
- `db/mongo_handler.py` - Database operations
- `gui/trend_tab.py` - Trend visualization from MongoDB
- `test_mongo.py` - Test database connection

### Test MongoDB:
```bash
python test_mongo.py
```

### Use the App:
1. Fill form and submit
2. Check `Trend Tracker` tab
3. Enter a Student ID
4. Click `Refresh` to see historical trend chart

**Phase 3 Complete when:**
- ✅ Submissions save to MongoDB Compass
- ✅ Trend Tracker shows a line chart
- ✅ Multiple submissions show trend progression

---

## File-by-File Execution Order

### Just Try ML Backend:
```bash
python data/eda.py                    # Explore data
python data/eda_visualizations.py     # Generate plots
python models/preprocess.py           # Split & scale data
python models/train_models.py         # Train models
python models/shap_analysis.py        # Generate explanations
python test_predictor.py              # Quick prediction test
```

### Run Full GUI:
```bash
python main.py                        # Opens 3-tab GUI
```

### Integration Test:
```bash
python test_mongo.py                  # Verify MongoDB connection
```

---

## Key Design Decisions

### No plt.show() in Backend
✅ All visualizations use `plt.savefig()` + `plt.close(fig)`  
❌ Never use `plt.show()` - it blocks the GUI

### ImageTk Garbage Collection
✅ Store PhotoImage on widget: `self.shap_lbl.image = photo`  
❌ Don't use local variables - image gets deleted

### Data Leakage Prevention
✅ Scale AFTER train/test split (fit scaler only on X_train)  
❌ Never scale full dataset before splitting

### Module-Level Imports in predictor.py
✅ Load models once at module level, reuse for all predictions  
❌ Don't reload models inside the predict() function

---

## Troubleshooting

**"Feature mismatch" error in predictor.py:**
- Make sure form field names match feature_names.pkl
- Run: `python -c "import joblib; print(joblib.load('models/feature_names.pkl'))"`

**SHAP image is blank:**
- Ensure `self.shap_lbl.image = photo` is set (prevents garbage collection)

**MongoDB connection refused:**
- Verify mongod is running: `ps aux | grep mongod`
- On Mac: `brew services list`

**Tkinter window freezes:**
- Check that grid() and pack() aren't mixed in same container
- Use `self.frame.update()` to force GUI refresh during long operations

---

## Next Steps

- Add user authentication
- Deploy to web (Flask + React frontend)
- Integrate with college notifications system
- Add counselor dashboard for faculty

