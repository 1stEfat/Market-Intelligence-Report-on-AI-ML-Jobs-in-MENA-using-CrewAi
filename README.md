# Market-Intelligence-Report-on-AI-ML-Jobs-in-MENA

# MENA AI/ML Job Market Analysis

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![CrewAI](https://img.shields.io/badge/Framework-CrewAI-orange.svg)
![Claude3](https://img.shields.io/badge/LLM-Claude%203-skyblue.svg)

A automated research system that analyzes AI/ML job trends across the Middle East and North Africa (MENA) region using Claude 3 and CrewAI.

## 📌 Features

- **Market Intelligence Pipeline**:
  - Scrapes job platforms (LinkedIn, Bayt, Wuzzuf)
  - Extracts 100+ job postings daily
  - Normalizes job titles and skills

- **Advanced Analytics**:
  - Identifies top demanded skills
  - Compares salary ranges by country
  - Detects emerging roles (AI Ethics, Prompt Engineering)

- **Automated Reporting**:
  - Generates markdown/PDF reports
  - Creates data visualizations
  - Updates weekly via scheduled runs

## 🛠️ Tech Stack

| Component       | Technology               |
|-----------------|--------------------------|
| LLM             | Anthropic Claude 3 Sonnet|
| Framework       | CrewAI                   |
| Search Tools    | Tavily, SerperDev        |
| Data Processing | Pandas, NumPy           |
| Visualization   | Matplotlib, Seaborn      |

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install crewai langchain-anthropic tavily-python pandas matplotlib pdfkit
