# 🧠 SlateMate AI – Safe & Personalized Web Feed

This project is a prototype AI system designed for SlateMate’s **FocusSphere** engine. It accepts a user-defined interest (e.g., `"Chess"`), analyzes an input content feed, scores each item for **relevance** and **toxicity**, and returns a **personalized, detoxified recommendation list**.

---

## 🎯 Features

- ✅ User-defined interest profiling using semantic embeddings (SBERT)
- ✅ Ingests a real content feed from an Excel file
- ✅ Calculates content relevance using cosine similarity
- ✅ Applies a safety filter based on toxicity score
- ✅ Combines both into a **Well-being Score** (wellbeing_score = relevance_score * (1 - toxicity_score) * 100)
- ✅ Returns top 5 recommendations and blocks unsafe/irrelevant content
- ✅ Bonus: Contextual “nudge” message for engagement

---

## 📂 Project Structure

- `app.py` — Streamlit-based interactive UI
- Input: Excel file (`.xlsx`) with columns: `title`, `text`, `source`, `toxicity_score`
- Output: Displayed recommendations, blocked content, and score breakdown

---

## 💻 How to Run

### 🔧 Requirements
Install dependencies with:
```bash
pip install streamlit sentence-transformers scikit-learn pandas openpyxl
**HOW TO RUN **
In the terminal :
streamlit run app.py



