# DharmaSetu – AI Legal Research Assistant

An AI-powered legal research assistant built as a B.Tech capstone project.  
**For educational purposes only — not legal advice.**

---

## Features
- Role-based explanations: Judge, Lawyer, Student
- Case analysis: issues, concepts, evidence, explanation
- Multi-language support: English, Hindi, Telugu
- Example query buttons for quick testing

## Setup

### 1. Clone / download the project

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API key
```bash
cp .env.example .env
# Edit .env and add your Groq API key
```
Get a free API key at https://console.groq.com

### 4. Run the app
```bash
streamlit run streamlit_app.py
```

## Project Structure
```
DharmaSetu/
├── streamlit_app.py   # Streamlit UI
├── main.py            # App config and constants
├── legal_engine.py    # AI case analysis logic
├── translation.py     # Language support
├── requirements.txt
├── README.md
└── .env.example
```

## Example Case (Built-in)
Two neighboring families had a dispute. A boy used abusive language toward two girls.  
The girls' father physically assaulted the boy. After one month, the boy's grandmother  
reported the incident to police with a video recording as evidence.

**Legal issues covered:** verbal harassment, physical assault, delayed video evidence.

## Disclaimer
This tool is for legal education and awareness only.  
It does not provide legal advice or render any verdict.
