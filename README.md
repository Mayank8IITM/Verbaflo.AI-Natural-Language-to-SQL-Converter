# Verbaflo.AI – Natural Language to SQL Web App

This Project I created for Verbaflo.ai <br> It's an AI-powered web application that allows users to **query business data in plain English** and get results directly from the database.  
This eliminates the need for SQL expertise, empowering business owners and analysts to extract insights effortlessly.  

---

## 🚀 Features
- 🗣️ **English → SQL Conversion** using AI (LangChain + OpenAI/LLM).
- 🛢️ **Database Integration** with SQLite (easily extendable to PostgreSQL/MySQL).
- 📊 **Instant Query Results** displayed as clean tables with optional charts.
- 🌐 **Streamlit Web Interface** – user-friendly and interactive.
- 🔒 **Secure Config Management** using `.env`.

---

## 🏗️ Project Structure
```
Verbaflo_AI/
│── app.py          # Streamlit app (main entry point)
│── db.py           # Database engine, sessions, and query helper
│── init_db.py      # Initializes & resets the database
│── models.py       # SQLAlchemy ORM models
│── nlsql.py        # Natural language → SQL conversion logic
│── prompts.py      # Prompt templates for NL→SQL
│── seed.py         # Seeds database with demo data
│── rental_app.db   # SQLite database (generated / included for testing)
│── requirements.txt# Python dependencies
│── README.md       # Project documentation (this file)
│── .env            # Environment variables (NOT included in repo)

```

## ⚙️ Installation & Setup

### 1. Clone Repository
```sh
git clone https://github.com/your-username/verbaflo-ai.git
cd verbaflo-ai
```
### 2. Create Virtual Environment
```sh
python3 -m venv .venv
source .venv/bin/activate   # For Mac/Linux
.venv\Scripts\activate      # For Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```sh
Create a `.env` file in the root directory:

GOOGLE_API_KEY="Your API Key"
DATABASE_URL=sqlite:///rental_app.db
MODEL_NAME=gemini-1.5-flash
```
### 5. Initialize Database
```sh
python init_db.py
```
### 6. Run the App
```sh
streamlit run app.py
```
---

## 📊 Example Usage

**Query (English):**
Who are the top 10 tenants by total rent paid?

**Generated SQL:**
```sh
SELECT T1.user_id, T1.first_name, T1.last_name, SUM(T2.amount) 
FROM users AS T1 
INNER JOIN payments AS T2 ON T1.user_id = T2.tenant_id 
WHERE T2.status = 'successful' 
GROUP BY T1.user_id 
ORDER BY SUM(T2.amount) 
DESC LIMIT 10
```
✅ Results are displayed in an interactive table in the Streamlit app.

---

## 🌐 Live Demo
You can try the deployed version here:  
👉 [Verbaflo.AI – Live App](your-streamlit-deployment-link)

---


## 📜 License
MIT License © 2025 

---

## 👨‍💻 Author
**Mayank Singh** – AI and Data Science @IIT Madras  
🔗 [LinkedIn](https://www.linkedin.com/in/mayank-singh-398148294/) | [GitHub](https://github.com/Mayank8IITM)
