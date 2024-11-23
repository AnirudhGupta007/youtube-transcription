import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from string import punctuation
from heapq import nlargest

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('stopwords')
except:
    pass

# Directly set the API keys
YOUTUBE_API_KEY = 'AIzaSyBPVOZSHEkyZn-8kqy9D_X6E4Bl6X0awpY'  # Replace with your actual YouTube API key

# Set Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Anirudh Gupta\Downloads\optimal-bivouac-429605-f8-014499c3d9b1.json"

def search_youtube(query):
    if not YOUTUBE_API_KEY:
        st.error("YouTube API key is not set.")
        return []
    
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=20
        )
        response = request.execute()
        return response['items']
    except Exception as e:
        st.error(f"Error in YouTube search: {str(e)}")
        return []

def get_transcripts(video_ids):
    transcripts = []
    for video_id in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcripts.append(' '.join([item['text'] for item in transcript]))
        except Exception as e:
            transcripts.append("Transcript not available")
    return transcripts

def summarize_text(text, num_sentences=5):
    try:
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)
        
        # Break the text into words
        words = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        stop_words = set(stopwords.words('english') + list(punctuation))
        word_freq = {}
        for word in words:
            if word not in stop_words:
                if word not in word_freq:
                    word_freq[word] = 1
                else:
                    word_freq[word] += 1
        
        # Calculate sentence scores based on word frequencies
        sentence_scores = {}
        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word_freq:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_freq[word]
                    else:
                        sentence_scores[sentence] += word_freq[word]
        
        # Get the summary (top N sentences)
        summary_sentences = nlargest(min(num_sentences, len(sentences)), 
                                   sentence_scores, 
                                   key=sentence_scores.get)
        
        # Join the sentences back together
        summary = ' '.join(summary_sentences)
        return summary
    except Exception as e:
        st.error(f"Error in summarization: {str(e)}")
        return "Summary not available"

st.title("YouTube Video Transcription and Summarization")

query = st.text_input("Enter search term:")
if query:
    videos = search_youtube(query)
    if videos:
        video_ids = [video['id']['videoId'] for video in videos]
        transcripts = get_transcripts(video_ids)
        summaries = [summarize_text(transcript) for transcript in transcripts]

        for i, video in enumerate(videos):
            st.subheader(video['snippet']['title'])
            with st.expander("Show Transcript"):
                st.text(transcripts[i][:500] + "...")  # Show first 500 characters of transcript
            with st.expander("Show Summary"):
                st.text(summaries[i])
            st.video(f"https://www.youtube.com/watch?v={video_ids[i]}")
    else:
        st.warning("No videos found for the given search term.")
else:
    st.info("Please enter a search term to find YouTube videos.")
