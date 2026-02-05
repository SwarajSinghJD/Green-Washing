# Greenwashing Detection System

An NLP-based system that analyzes real ESG and sustainability reports to detect potential greenwashing at the sentence level, using robust PDF preprocessing, weak supervision, and semantic models (BERT) to produce company-level greenwashing risk scores.

## Overview

This project addresses the growing concern of greenwashing in corporate sustainability reporting by automatically analyzing ESG (Environmental, Social, and Governance) reports to identify vague, unsubstantiated, or misleading environmental claims.

## Features

- **PDF Text Extraction**: Automated extraction of text content from ESG reports using `pdfplumber`
- **Robust Text Cleaning**: Removal of structural artifacts (page markers, headers, footers) and noise from extracted documents
- **Weak Supervision Labeling**: Rule-based approach to classify sentences into:
  - **Evidence-based (0)**: Contains metrics and measurable indicators
  - **Grey-area (1)**: Action statements without concrete metrics
  - **Greenwashing-prone (2)**: Visionary/marketing language without substantiation
- **Multiple Model Approaches**:
  - TF-IDF + Logistic Regression baseline
  - Sentence-BERT embeddings
  - Fine-tuned BERT classifier
- **Company-level Risk Scoring**: Aggregation of sentence-level predictions into greenwashing risk percentages per company

## Data Pipeline

### 1. Text Extraction
```python
import pdfplumber

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text
```

### 2. Text Cleaning
- Remove page markers (`--- PAGE X ---`)
- Detect and remove repeated structural lines across documents
- Filter out short or invalid sentences
- Normalize spacing and formatting

### 3. Weak Supervision
Sentences are labeled based on:
- **Category** (vision/action/metric)
- **Presence of metrics** (numbers, percentages, concrete data)
- **Vague language indicators** (leading, significant, robust, etc.)
- **Future-oriented language** (will, aim, plan, target, etc.)

## Models

### Baseline: TF-IDF + Logistic Regression
- Feature extraction using TF-IDF (8000 features, 1-2 grams)
- Additional features: future word count, vague word count, has_metric flag
- Class-balanced logistic regression

### Sentence-BERT
- Pre-trained `all-MiniLM-L6-v2` model for semantic embeddings
- Dense representations capture contextual meaning

### Fine-tuned BERT
- Base model: `bert-base-uncased`
- Binary classification: greenwashing-prone vs. substantiated
- Training: 3 epochs, learning rate 2e-5, batch size 8
- Saved to: `greenwashing_app/model/bert_greenwashing`

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements
```
pandas
numpy
scikit-learn
torch
transformers
sentence-transformers
pdfplumber
nltk
matplotlib
datasets
scipy
```

## Usage

### 1. Extract Text from PDFs
Place your ESG PDFs in `dataset/extracted_text/` and run the extraction notebook cells.

### 2. Clean Extracted Text
Run `Text_Cleaning.ipynb` to:
- Detect repeated structural junk
- Remove page markers and formatting artifacts
- Save cleaned files to `dataset/cleaned_text/`

### 3. Train Models
Run `app.ipynb` to:
- Load and preprocess data
- Apply weak supervision labels
- Train baseline and advanced models
- Generate predictions

### 4. Generate Company Risk Scores
```python
# Predict greenwashing for all sentences
df_clean["gw_pred"] = model_bin.predict(tfidf.transform(df_clean["sentence"]))

# Aggregate by company
company_risk = (
    df_clean
    .groupby(["company", "year"])
    .gw_pred
    .mean()
    .reset_index(name="greenwashing_ratio")
)
```

## Project Structure

```
Greenwashing/
├── README.md
├── requirements.txt
├── app.ipynb                          # Main training and analysis notebook
├── Text_Cleaning.ipynb                # Text preprocessing pipeline
├── dataset/
│   ├── extracted_text/                # Raw extracted text from PDFs
│   │   ├── OTC_TATLY_2021_esg.txt
│   │   ├── NASDAQ_NVDA_2022_esg.txt
│   │   └── ...
│   ├── cleaned_text/                  # Cleaned and processed text
│   └── preprocessed_content.csv       # Combined and labeled dataset
├── greenwashing_app/
│   └── model/
│       └── bert_greenwashing/         # Fine-tuned BERT model
└── results/                           # Training checkpoints and logs
```

## Dataset

The project uses ESG and sustainability reports from various companies including:
- Tata Steel (OTC: TATLY)
- NVIDIA (NASDAQ: NVDA)
- Boeing (NYSE: BA)
- Murphy Oil (NYSE: MUR)
- Vedanta (NYSE: VEDL)
- And more...

Reports span multiple years (2016-2024) to analyze trends.

## Results

The system generates:
- **Sentence-level predictions**: Binary classification (greenwashing vs. substantiated)
- **Company-level risk scores**: Percentage of greenwashing-prone statements
- **Visualizations**: Bar charts showing comparative greenwashing percentages across companies

## Key Insights

The weak supervision approach allows scaling without extensive manual labeling by leveraging:
1. Presence of quantitative metrics
2. Future-oriented language patterns
3. Vague/marketing language indicators
4. Statement category (vision/action/metric)

## Future Improvements

- [ ] Expand dataset with more companies and industries
- [ ] Implement multi-class classification for greenwashing severity
- [ ] Add explainability features (attention visualization, SHAP values)
- [ ] Develop web interface for real-time analysis
- [ ] Incorporate temporal analysis to track changes over time
- [ ] Add benchmark against manual expert annotations

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is for research and educational purposes.

## Acknowledgments

- ESG reports from publicly traded companies
- Pre-trained models from Hugging Face
- Sentence-BERT framework for semantic embeddings
