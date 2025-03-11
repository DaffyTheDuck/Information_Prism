import streamlit as st
from rouge_score import rouge_scorer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Streamlit App Title
st.title("ROUGE Score Comparison")

# Model's input (Generated Text)
llm_model_input = st.text_area("Model's Response")

# User's input (Reference Text)
user_input = st.text_area("Reference Text (Ground Truth)")

# Button to calculate scores
calculate_button = st.button("Calculate ROUGE Scores", type='primary')

# Function to calculate ROUGE score
def calc_rouge_score(reference_text, predicted_text):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(predicted_text, reference_text)
    return {metric: score.fmeasure for metric, score in scores.items()}

if calculate_button:
    if llm_model_input and user_input:
        # Calculate ROUGE scores
        rouge_scores = calc_rouge_score(user_input, llm_model_input)

        # Convert scores to DataFrame for table format
        scores_df = pd.DataFrame.from_dict(rouge_scores, orient='index', columns=["F1 Score"]).reset_index()
        scores_df.rename(columns={"index": "ROUGE Metric"}, inplace=True)

        # Display ROUGE Scores in Table
        st.subheader("ROUGE Scores:")
        st.table(scores_df)

        # Visualization - Bar Chart
        metrics = list(rouge_scores.keys())
        values = list(rouge_scores.values())

        plt.figure(figsize=(8, 5))
        plt.bar(metrics, values, color=['blue', 'orange', 'green'])
        plt.ylim(0, 1)
        plt.xlabel("ROUGE Metrics")
        plt.ylabel("Score (F1)")
        plt.title("ROUGE Score Visualization")
        st.pyplot(plt)

        # Visualization - Heatmap
        plt.figure(figsize=(6, 4))
        score_matrix = np.array(values).reshape(1, -1)
        sns.heatmap(score_matrix, annot=True, cmap="coolwarm", xticklabels=metrics, yticklabels=["Scores"], cbar=False)
        plt.title("ROUGE Score Heatmap")
        st.pyplot(plt)

        # Visualization - Line Chart
        plt.figure(figsize=(8, 5))
        plt.plot(metrics, values, marker='o', linestyle='-', color='b')
        plt.ylim(0, 1)
        plt.xlabel("ROUGE Metrics")
        plt.ylabel("Score (F1)")
        plt.title("ROUGE Score Trends")
        plt.grid(True)
        st.pyplot(plt)

    else:
        st.warning("Please enter both Model's Response and Reference Text.")