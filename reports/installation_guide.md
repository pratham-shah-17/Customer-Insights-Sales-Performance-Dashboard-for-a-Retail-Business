# Installation & Deployment Guide

This guide details the technical prerequisites, installation steps, cloud deployment configurations, and troubleshooting procedures required to host the Customer Insights & Sales Performance Dashboard.

---

## 1. System Requirements & Prerequisites

### Hardware Requirements
* **Processor**: Dual-core CPU (Quad-core recommended for model training)
* **RAM**: 8 GB minimum (16 GB recommended)
* **Storage**: 1 GB free space (to store model pickles, visualizations, and datasets)

### Software Prerequisites
* **Operating System**: Windows 10/11, macOS Big Sur+, or Linux (Ubuntu 20.04 LTS+)
* **Python Environment**: Python 3.9, 3.10, or 3.11. (Python 3.12+ can experience wheel compilation bottlenecks for scikit-learn/xgboost on certain systems).
* **Git**: Installed for cloning repositories and version control.

---

## 2. Local Environment Installation

Follow these steps to set up the project on your local machine:

### Step 2.1: Clone/Copy the Codebase
Ensure your workspace contains the correct folders:
```bash
cd "C:/Users/Pratham/Desktop/AI startup founder Simulator"
```

### Step 2.2: Set Up Virtual Environment (Highly Recommended)
Creating a virtual environment isolates project dependencies to avoid conflicts with global libraries:

* **Windows**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 2.3: Install Packages
Install packages specified in `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Running the Complete Analytics Pipeline

To ingest data, preprocess, execute RFM segmentation, train predictive ML models, and generate insights programmatically:

1. **Ingest relational data**:
   ```bash
   python src/data_ingestion.py
   ```
2. **Preprocess and merge tables**:
   ```bash
   python src/data_cleaning.py
   ```
3. **Execute EDA engine**:
   ```bash
   python src/eda_engine.py
   ```
4. **Train ML models**:
   ```bash
   python src/ml_pipeline.py
   ```
5. **Generate insights report**:
   ```bash
   python src/insights_engine.py
   ```
6. **Compile PPT presentation slides**:
   ```bash
   python presentation/generate_ppt.py
   ```

---

## 4. Launching the Interactive Web Dashboard

Streamlit hosts the interactive dashboard locally:
```bash
streamlit run src/streamlit_app.py
```
The console will display:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```
Open `http://localhost:8501` to access the application.

---

## 5. Production Cloud Deployment

### 5.1 Streamlit Community Cloud (Recommended & Free)
Streamlit Cloud offers seamless deployment directly from GitHub:
1. Push your local project to a public **GitHub** repository.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New App**.
4. Select your **Repository**, **Branch** (usually `main`), and enter `src/streamlit_app.py` as the **Main file path**.
5. Click **Deploy**. Streamlit Cloud will parse `requirements.txt` and host the app automatically.

### 5.2 Docker Containerization
To deploy on enterprise cloud platforms (AWS ECS, Google Cloud Run, Azure App Services), package the app in a Docker container:

Create a `Dockerfile` at the root of the project:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose default Streamlit port
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run the container locally:
```bash
docker build -t retail-dashboard .
docker run -p 8501:8501 retail-dashboard
```

---

## 6. Troubleshooting & Common Issues

### Issue 1: `ModuleNotFoundError`
* **Cause**: Packages are not installed in the active environment.
* **Solution**: Ensure your virtual environment is activated, then run `pip install -r requirements.txt`.

### Issue 2: `sklearn` / `xgboost` installation errors
* **Cause**: Missing C++ compilation tools on Windows.
* **Solution**: Standard wheels are available for Python 3.9, 3.10, and 3.11. If using Python 3.12+, run a pip install using precompiled binaries or install the Visual C++ Build Tools from Microsoft.

### Issue 3: Streamlit app runs out of memory
* **Cause**: Caching too much data in RAM.
* **Solution**: The `@st.cache_data` decorator is applied to `load_data()` in `streamlit_app.py` to prevent redundant reload executions. If deploying to tiny cloud instances, reduce the number of historical records processed in `raw_superstore.csv`.
