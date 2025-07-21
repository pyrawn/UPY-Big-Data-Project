# UPY-Big-Data-Project

This project is a **Batch Processing ETL Pipeline** using Apache Airflow as the orchestration tool. It extracts data from three public APIs, processes it, and loads it into a MongoDB Data Warehouse. The processed data is visualized via multiple dashboards in Streamlit, with each dashboard accessible through separate pages in the app UI.

---

## 📂 Project Structure

```
.
├── dags/                  # Airflow DAGs for ETL process
│   └── utils/
├── app/
│   ├── requirements.txt
│   ├── Dockerfile            # Streamlit app with dashboards
│   ├── pages/        # Individual dashboards per API
│   └── app.py             # Main Streamlit application
├── .gitignore
├── docker-compose.yml     # Orchestration of all containers
├── README.md              # Project documentation
└── Dockerfile
```

---

## ⚙️ Technologies Used

- **Orchestration:** Apache Airflow
- **Database:** MongoDB, PostgreSQL
- **Data Visualization:** Streamlit
- **Containerization:** Docker, Docker Compose
- **Libraries:**
    - **Python:** pandas, pymongo, requests, beautifulsoup4, lxml, wordcloud, matplotlib, Pillow, plotly, tabulate

---

## 🛡️ Data Sources

### 🕵️ FBI Wanted Persons

- **Theme:** Public Security
- **API Name:** FBI Wanted API
- **API Link:** [https://api.fbi.gov/wanted/v1/list](https://api.fbi.gov/wanted/v1/list)
- **Description:** Provides data about people wanted by the FBI including names, images, crimes, and status.

---

### 💼 ArbeitNow Job Board

- **Theme:** Global Job Market
- **API Name:** ArbeitNow Job Board API
- **API Link:** [https://www.arbeitnow.com/api/job-board-api](https://api.arbeitnow.com/api/job-board-api)
- **Description:** Contains job postings from various countries with details like title, location, company, and remote availability.

---

### 🚀 Spaceflight News API

- **Theme:** Space Exploration and Technology
- **API Name:** Spaceflight News API
- **API Link:** [https://api.spaceflightnewsapi.net/v4/articles](https://api.spaceflightnewsapi.net/v4/articles)
- **Description:** Offers up-to-date articles about spaceflight missions, agencies, and technological advances.

---

## 💾 App Overview

The Streamlit application is organized into multiple sections:

### 🌐 Welcome Page

- Displays project overview and purpose.
- Explains how the dashboards reflect different aspects of global societal data.

---

### 📊 Dashboards

#### 1️⃣ Public Security Dashboard

- **Theme:** Analyzing wanted persons by the FBI.
- **Data Source:** FBI Wanted API
- **Features:**

  - Overview of wanted individuals.
  - Filters for crime type, status (captured / uncaptured), and years.
  - Interactive components to explore profiles.

---

#### 2️⃣ Job Market Dashboard

- **Theme:** Visualizing global employment trends.
- **Data Source:** ArbeitNow Job Board API
- **Features:**

  - Job availability by country and sector.
  - Filters for job type (remote/on-site), industry, and location.
  - Insights into global hiring patterns.

---

#### 3️⃣ Space Exploration Dashboard

- **Theme:** Tracking spaceflight news and innovations.
- **Data Source:** Spaceflight News API
- **Features:**

  - Timeline of recent articles.
  - Filters for space agencies and date ranges.
  - Overview of space exploration trends.

---

### 📝 Menu Layout

- Welcome
- 🕵️ Public Security
- 💼 Job Market
- 🚀 Space Exploration

Each menu item navigates to a dedicated dashboard page.

---

## ⚙️ Orchestration Pipeline

### 🌀 Airflow DAGs

The ETL process is managed through Airflow. The project includes both individual and a unified DAG:

- **Individual DAGs:**
    - `fbi_dag.py`: Extracts, transforms, and loads data from the FBI Wanted API.
    - `arbeitnow_dag.py`: Extracts, transforms, and loads data from the ArbeitNow Job Board API.
    - `spaceflight_dag.py`: Extracts, transforms, and loads data from the Spaceflight News API.
- **Unified DAG:**
    - `pipeline_dag.py`: A unified DAG that orchestrates the entire ETL pipeline, running the extraction, transformation, and loading tasks for all three APIs in a coordinated manner.

### 🔄 Workflow

1. **Extract:** Pulls raw JSON data from APIs.
2. **Transform:** Cleans and structures data for analysis.
3. **Load:** Inserts transformed data into MongoDB collections.

---

## 🗃️ Data Warehouse

The project uses MongoDB as the primary data warehouse for storing the transformed data from the APIs. Additionally, it utilizes a PostgreSQL database as the backend for Apache Airflow to store metadata, DAG schedules, and task history.

### MongoDB

The MongoDB Data Warehouse consists of three collections:

| Collection Name  | Source API              |
| ---------------- | ----------------------- |
| `fbi_wanted`     | FBI Wanted API          |
| `arbeitnow_jobs`     | ArbeitNow Job Board API |
| `space_news` | Spaceflight News API    |

Each collection contains cleaned JSON documents ready for visualization.

### PostgreSQL

The PostgreSQL database is used exclusively by Airflow for its operational needs. It does not store any data from the ETL pipeline.

---

## 🛡️ Containerization

### 📦 Docker Compose

The entire stack is containerized with Docker:

- **MongoDB:** Data Warehouse
- **PostgreSQL:** Airflow Backend
- **Airflow Webserver & Scheduler:** ETL Orchestration
- **Streamlit App:** Data Visualization

---

### 💻 How to Run

1. Clone the repository:

```bash
git clone <repo_url>
cd UPY-Big-Data-Project
```
2. Docker initialization 
Ensure you have Docker Desktop installed and running.
If you are in MacOs/Linux:
```bash
docker-compose run --rm webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow
```
If you are in Windows Powershell:
```bash
docker-compose run --rm webserver airflow users create `
    --username airflow `
    --firstname Admin `
    --lastname User `
    --role Admin `
    --email admin@example.com `
    --password airflow
```

3. Build and run containers:

```bash
docker-compose up --build
```

4. Access Airflow UI:

```bash
http://localhost:8080
```

5. Access Streamlit App:

```bash
http://localhost:8501
```
6. MongoDB Compass Connection:
```js
mongodb://root:example@localhost:27018/admin
```

---