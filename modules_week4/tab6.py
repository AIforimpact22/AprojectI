import streamlit as st

def show():
    st.markdown("<h1 style='color: #98FB98;'>4.5 Understanding and Working with Text Data</h1>", unsafe_allow_html=True)
    st.markdown("### What is Text Data?")
    st.image("photos/17.png")
    st.markdown(
        """
Text data refers to any written or spoken digital content. It includes customer reviews, academic papers, and social media posts.
        """
    )
    st.markdown("### Why It Matters")
    st.image("photos/18.png")
    st.markdown(
        """
Text data provides insights into human sentiment, enables automation, and supports real-time decision making.
        """
    )
    st.markdown("### Applications of Text Data")
    st.markdown(
        """
1. **Customer Feedback Analysis**  
   - Analyze reviews to identify strengths and weaknesses.
2. **Summarizing Research**  
   - Condense lengthy papers into actionable summaries.
3. **Chatbot Development**  
   - Train AI models for natural language interactions.
        """
    )
    st.markdown("### Key Tools and Frameworks for Text Data")
    st.image("photos/19.png")
    st.markdown(
        """
1. **NLTK:** Tokenization, stemming, sentiment analysis.
2. **Hugging Face Transformers:** Advanced text generation, classification, and summarization.
3. **SpaCy:** Named Entity Recognition and dependency parsing.
        """
    )
    st.markdown("### Example Datasets")
    st.markdown(
        """
**Customer Reviews**, **Summarized Research**, and **Chatbot Training Data** tables.
        """
    )
    st.markdown("### How to Work With Text Data")
    st.image("photos/20.png")
    st.markdown(
        """
- **Data Acquisition:** Use Kaggle, Google Dataset Search, or Twitter API.
- **Preprocessing:** Tokenization and cleaning using NLTK or SpaCy.
- **Advanced Analysis:** Sentiment analysis and summarization with Hugging Face Transformers.
- **Visualization:** Word clouds and sentiment trend plots.
        """
    )
    st.markdown("### References")
    st.markdown(
        """
- [NLTK Documentation](https://www.nltk.org/)  
- [Hugging Face Transformers](https://huggingface.co/transformers/)  
- [Google AI Blog on Text Summarization](https://ai.googleblog.com/)  
- [Kaggle Case Studies](https://www.kaggle.com/)  
- [Twitter Developer Documentation](https://developer.twitter.com/)
        """
    )
