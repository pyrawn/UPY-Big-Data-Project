# UPY-Big-Data-Project

This project is a **Batch Processing ETL Pipeline** using Apache Airflow as the orchestration tool. It extracts data from three public APIs, processes it, and loads it into a MongoDB Data Warehouse. The processed data is visualized via multiple dashboards in Streamlit, with each dashboard accessible through separate pages in the app UI.

---

## 📂 Project Structure

```
.
├── dags/                  # Airflow DAGs for ETL process
├── app/                   # Streamlit app with dashboards
│   ├── dashboards/        # Individual dashboards per API
│   └── app.py             # Main Streamlit application
├── mongo_data/            # MongoDB persistent storage
├── docker-compose.yml     # Orchestration of all containers
├── README.md              # Project documentation
└── .env.example           # Environment variables (if needed)
```

---

## 🛡️ Data Sources

### 🕵️ FBI Wanted Persons

* **Theme:** Public Security
* **API Name:** FBI Wanted API
* **API Link:** [https://api.fbi.gov/wanted/v1/list](https://api.fbi.gov/wanted/v1/list)
* **Description:** Provides data about people wanted by the FBI including names, images, crimes, and status.

---

### 💼 ArbeitNow Job Board

* **Theme:** Global Job Market
* **API Name:** ArbeitNow Job Board API
* **API Link:** [https://www.arbeitnow.com/api/job-board-api](https://www.arbeitnow.com/api/job-board-api)
* **Description:** Contains job postings from various countries with details like title, location, company, and remote availability.

---

### 🚀 Spaceflight News API

* **Theme:** Space Exploration and Technology
* **API Name:** Spaceflight News API
* **API Link:** [https://api.spaceflightnewsapi.net/v4/articles](https://api.spaceflightnewsapi.net/v4/articles)
* **Description:** Offers up-to-date articles about spaceflight missions, agencies, and technological advances.

---

## 💾 App Overview

The Streamlit application is organized into multiple sections:

### 🌐 Welcome Page

* Displays project overview and purpose.
* Explains how the dashboards reflect different aspects of global societal data.

---

### 📊 Dashboards

#### 1️⃣ Public Security Dashboard

* **Theme:** Analyzing wanted persons by the FBI.
* **Data Source:** FBI Wanted API
* **Features:**

  * Overview of wanted individuals.
  * Filters for crime type, status (captured / uncaptured), and years.
  * Interactive components to explore profiles.

---

#### 2️⃣ Job Market Dashboard

* **Theme:** Visualizing global employment trends.
* **Data Source:** ArbeitNow Job Board API
* **Features:**

  * Job availability by country and sector.
  * Filters for job type (remote/on-site), industry, and location.
  * Insights into global hiring patterns.

---

#### 3️⃣ Space Exploration Dashboard

* **Theme:** Tracking spaceflight news and innovations.
* **Data Source:** Spaceflight News API
* **Features:**

  * Timeline of recent articles.
  * Filters for space agencies and date ranges.
  * Overview of space exploration trends.

---

### 📝 Menu Layout

* Welcome
* 🕵️ Public Security
* 💼 Job Market
* 🚀 Space Exploration

Each menu item navigates to a dedicated dashboard page.

---

## ⚙️ Orchestration Pipeline

### 🌀 Airflow DAGs

The ETL process is managed through Airflow. Each API has its own DAG:

* `fbi_etl.py`: Extracts data from FBI Wanted API.
* `jobs_etl.py`: Extracts job data from ArbeitNow.
* `space_etl.py`: Extracts news articles from Spaceflight News API.

### 🔄 Workflow

1. **Extract:** Pulls raw JSON data from APIs.
2. **Transform:** Cleans and structures data for analysis.
3. **Load:** Inserts transformed data into MongoDB collections.

---

## 💄 Data Warehouse

The MongoDB Data Warehouse consists of three collections:

| Collection Name  | Source API              |
| ---------------- | ----------------------- |
| `fbi_wanted`     | FBI Wanted API          |
| `job_market`     | ArbeitNow Job Board API |
| `space_articles` | Spaceflight News API    |

Each collection contains cleaned JSON documents ready for visualization.

---

## 🛡️ Containerization

### 📦 Docker Compose

The entire stack is containerized with Docker:

* **MongoDB:** Data Warehouse
* **Airflow Webserver & Scheduler:** ETL Orchestration
* **Streamlit App:** Data Visualization

---

### 💻 How to Run

1. Clone the repository:

```bash
git clone <repo_url>
cd UPY-Big-Data-Project
```

2. Build and run containers:

```bash
docker-compose up --build
```

3. Access Airflow UI:

```bash
http://localhost:8080
```

4. Access Streamlit App:

```bash
http://localhost:8501
```

---

## 🔥 Extra Sections

### 📜 API Documentation

Each API endpoint and fields are documented in `/dags/utils/api_helpers.py` for reference.

### 📊 KPI Calculations

The assistant will compute KPIs dynamically based on:

* Count of records.
* Aggregated values (e.g., job counts, articles per agency).
* Filtered queries from MongoDB.

---
