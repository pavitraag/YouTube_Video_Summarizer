import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

# Function to get the transcript from YouTube
def get_transcript(youtube_url):
    video_id = youtube_url.split("v=")[-1]
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try fetching the manual transcript
        try:
            transcript = transcript_list.find_manually_created_transcript()
        except:
            # Try fetching the generated transcript in English
            transcript = transcript_list.find_generated_transcript(['en'])
        
        # Combine the transcript text
        full_transcript = " ".join([part['text'] for part in transcript.fetch()])
        
        if not full_transcript:
            raise Exception("Transcript is empty.")
        
        return full_transcript

    except Exception as e:
        raise Exception("No suitable transcript found for this video.")

# Function to summarize using Hugging Face model
def summarize_text(transcript):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Hugging Face models work better with smaller text sizes, so limit the transcript size
    max_input_length = 1024  # BART model input size limit
    short_transcript = transcript[:max_input_length]  # Truncate the transcript if it's too long
    
    # Summarize the shortened transcript with adjusted lengths for a longer summary
    summary = summarizer(short_transcript, max_length=300, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# Streamlit UI
def main():
    st.title('YouTube Video Summarizer without API Key')
    link = st.text_input('Enter the YouTube video link you want to summarize:')
    
    if st.button('Start'):
        if link:
            try:
                progress = st.progress(0)
                status_text = st.empty()

                status_text.text('Loading the transcript...')
                progress.progress(25)

                # Get the YouTube transcript
                transcript = get_transcript(link)

                status_text.text('Summarizing the video...')
                progress.progress(75)

                # Summarize the transcript
                summary = summarize_text(transcript)

                status_text.text('Summary:')
                st.markdown(summary)
                progress.progress(100)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning('Please enter a valid YouTube link.')

if __name__ == "__main__":
    main()
