import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import json

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# ---------- Module 1: Interest Vectorizer ----------
def get_interest_vector(interest: str):
    interest_sentence = f"This content is about {interest}."
    return model.encode(interest_sentence)

# ---------- Module 2: Load Content Feed from File ----------
def load_content_feed(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df.dropna(subset=['title', 'text', 'source', 'toxicity_score'])
    feed = df.to_dict(orient='records')
    return feed, df

# ---------- Module 3: Relevance & Safety Scoring ----------
def compute_relevance_score(item, interest_vector):
    full_text = f"{item['title']}. {item['text']}. This content is from {item['source']}."
    content_vector = model.encode(full_text)
    return cosine_similarity([interest_vector], [content_vector])[0][0]

def compute_wellbeing_score(relevance, toxicity):
    return round((relevance * (1 - toxicity)) * 100, 2)

def re_rank_feed(user_interest: str, feed: list):
    interest_vec = get_interest_vector(user_interest)
    ranked = []

    for item in feed:
        rel = compute_relevance_score(item, interest_vec)
        well_score = compute_wellbeing_score(rel, item["toxicity_score"])
        item["relevance_score"] = round(rel, 3)
        item["wellbeing_score"] = well_score
        ranked.append(item)

    return sorted(ranked, key=lambda x: x["wellbeing_score"], reverse=True)

# ---------- Module 4: Output Engine ----------
def generate_safe_feed(user_interest: str, content_feed: list) -> dict:
    re_ranked = re_rank_feed(user_interest, content_feed)
    recommendations = []
    blocked_irrelevant = []
    blocked_toxic = []

    for item in re_ranked:
        reason = ""
        if item["relevance_score"] < 0.3:
            reason = "Low relevance to interest"
            blocked_irrelevant.append({"title": item["title"], "reason": reason})
        elif item["toxicity_score"] > 0.35:
            reason = "Potentially unsafe content"
            blocked_toxic.append({"title": item["title"], "reason": reason})
        else:
            reason = "Highly relevant & safe" if item["wellbeing_score"] > 60 else "Moderately relevant"
            recommendations.append({
                "title": item["title"],
                "source": item["source"],
                "wellbeing_score": item["wellbeing_score"],
                "reason": reason
            })

    return {
        "detected_interest": user_interest,
        "top_recommendations": recommendations,
        "blocked_content_irrelevant": blocked_irrelevant,
        "blocked_content_toxic": blocked_toxic,
        "all_ranked": re_ranked
    }

# ---------- Streamlit UI ----------
st.set_page_config(page_title="SlateMate AI - Safe Feed Generator", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; padding: 20px; border-radius: 10px; }
    .block-section { background-color: #fff3f3; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    .recommendation-card { background-color: #f0f9ff; padding: 15px; border-left: 5px solid #007acc; margin-bottom: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 SlateMate: Safe & Personalized Web Feed")

user_interest = st.text_input("🎯 Enter your interest (e.g., Chess, Robotics):")
uploaded_file = st.file_uploader("📂 Upload content feed Excel file", type=["xlsx"])

if st.button("🔎 Generate Safe Feed") and user_interest and uploaded_file:
    feed, df = load_content_feed(uploaded_file)
    result = generate_safe_feed(user_interest, feed)

    st.markdown("## 🎯 Top Recommendations")
    top_recs = result["top_recommendations"][:5]
    for rec in top_recs:
        st.markdown(f"<div class='recommendation-card'><strong>{rec['title']}</strong><br><em>Source:</em> {rec['source']}<br><strong>Score:</strong> {rec['wellbeing_score']}<br><small>{rec['reason']}</small></div>", unsafe_allow_html=True)

    if result["blocked_content_irrelevant"]:
        st.markdown("## 🚫 Blocked: Low Relevance")
        to_show_irrelevant = result["blocked_content_irrelevant"][:5]
        for blk in to_show_irrelevant:
            st.markdown(f"<div class='block-section'>❌ <strong>{blk['title']}</strong><br><small>{blk['reason']}</small></div>", unsafe_allow_html=True)

    if result["blocked_content_toxic"]:
        st.markdown("## ⚠️ Blocked: Toxic Content")
        to_show_toxic = result["blocked_content_toxic"][:5]
        for blk in to_show_toxic:
            st.markdown(f"<div class='block-section'>☠️ <strong>{blk['title']}</strong><br><small>{blk['reason']}</small></div>", unsafe_allow_html=True)

    st.success(f"💡 Nudge: New {user_interest.lower()} video found: ‘Mastering Queen's Gambit’ 🎯")


