import streamlit as st
from comments import fetch_comments
from twitter_comments import (
    initialize_twitter_client_v2,
    extract_tweet_id_from_url,
    fetch_tweet_replies,
    load_replies_in_format,
    summarize_replies,
    categorize_replies
)
from utils import get_summary
import base64
from transformers import pipeline
import re
import tweepy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page configuration
st.set_page_config(page_title="EchoPulse | Comment Analyzer", layout="wide")

# Add custom CSS for styling
def add_custom_styles():
    custom_css = r"""
    <style>
        /* General styling */
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        body, html {
            background-color: #0E1117;
            margin: 0;
            padding: 0;
            width: 100%;
        }
        
        /* --- Navigation Bar --- */
        .nav-links {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px 0;
            background: rgba(14, 17, 23, 0.85);
            backdrop-filter: blur(10px);
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 100;
            border-bottom: 1px solid #262730;
        }
        .nav-links a {
            color: #FAFAFA;
            text-decoration: none;
            font-size: 1.1rem;
            padding: 10px 20px;
            margin: 0 10px;
            border-radius: 8px;
            transition: background-color 0.3s, color 0.3s;
        }
        .nav-links a:hover {
            background-color: #0063B2;
            color: white;
        }

        /* --- Banner & Video --- */
        .banner {
            position: relative;
            height: 100vh;
            width: 100%;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #background-video {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transform: translate(-50%, -50%);
            z-index: -1;
            opacity: 0.3;
        }
        .content {
            text-align: center;
            color: white;
            z-index: 1;
        }
        .content h1 {
            font-size: 3.5rem;
            font-weight: bold;
            color: white;
        }
        .content p {
            font-size: 1.5rem;
            color: #CFCFCF;
        }

        /* --- Section Styling --- */
        section {
            padding-top: 100px; /* Offset for fixed navbar */
            margin-top: -80px;
        }
        
        /* --- General UI Elements --- */
        .stButton button {
            background-color: #0063B2;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            border: none;
        }
        .stButton button:hover {
            background-color: #0079D6;
        }
        .stTextInput input {
            border-radius: 8px;
        }

        /* --- About Us Cards --- */
        .cards-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 25px;
            margin-top: 20px;
            padding: 10px;
        }
        .card {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 10px;
            width: 320px;
            text-align: center;
            padding: 25px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 8px 30px rgba(0, 99, 178, 0.5);
        }
        .card img {
            width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .card h3 {
            font-size: 20px;
            color: #FAFAFA;
            margin: 20px 0 10px;
        }
        .card p {
            font-size: 14px;
            color: #CFCFCF;
            line-height: 1.6;
        }

        /* --- Footer --- */
        footer {
            text-align: center;
            padding: 20px 0;
            background: rgba(14, 17, 23, 0.85);
            width: 100%;
            color: #CFCFCF;
            margin-top: 50px;
            border-top: 1px solid #262730;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

add_custom_styles()

# Header navigation
st.markdown(
    """
    <div class="nav-links">
        <a href="#home">Home</a>
        <a href="#analyzer">Analyzer</a>
        <a href="#about-us">About</a>
        <a href="#contact-us">Contact</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Function to encode video to Base64
@st.cache_data
def video_to_base64(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode()

video_base64 = video_to_base64("static/bg.mp4")

# Home Section
st.markdown('<section id="home"></section>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="banner">
        <video autoplay muted loop id="background-video">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div class="content">
            <h1>EchoPulse</h1>
            <p>Amplify Your Audience's Voice. Instant Insights from Social Comments.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Analyzer Section
st.markdown('<section id="analyzer"></section>', unsafe_allow_html=True)
st.title("Comment Analyzer")
st.write("Select a platform to analyze comments and generate AI-powered summaries.")

youtube_tab, twitter_tab = st.tabs(["YouTube", "Twitter"])

with youtube_tab:
    st.header("Analyze YouTube Comments")
    
    left, right = st.columns(2)
    with left:
        with st.form("youtube_form"):
            url_input = st.text_input(
                "Enter YouTube video URL",
                placeholder="Paste your YouTube video link here...",
            )
            submit_youtube = st.form_submit_button("Get Summary")

    with right:
        if submit_youtube and url_input:
            with st.spinner("Fetching and summarizing comments..."):
                text = fetch_comments(url_input)
                if text:
                    final_summary = get_summary(text)
                    st.subheader("Generated Summary")
                    st.markdown(f"<div style='font-size:16px; line-height:1.6;'>{final_summary}</div>", unsafe_allow_html=True)
                else:
                    st.error("Unable to fetch comments. The video might have comments disabled or the URL is invalid.")
        else:
            st.info("Submit a YouTube URL to display its summary here.")

with twitter_tab:
    st.header("Analyze Twitter Replies")
    
    left, right = st.columns(2)
    with left:
        with st.form("twitter_form"):
            tweet_url = st.text_input(
                "Enter Tweet URL",
                placeholder="Paste the tweet URL here...",
            )
            max_results = st.slider("Number of Comments to fetch", 10, 100, 25)
            submit_tweet = st.form_submit_button("Get Summary")

    with right:
        if submit_tweet and tweet_url:
            with st.spinner("Fetching and summarizing replies..."):
                tweet_id = extract_tweet_id_from_url(tweet_url)
                if tweet_id:
                    client = initialize_twitter_client_v2()
                    comments = fetch_tweet_replies(client, tweet_id, max_replies=max_results)
                    if comments:
                        summary = summarize_replies(comments)
                        st.subheader("Summary of Replies")
                        st.write(summary)
                    else:
                        st.error("No replies found or an error occurred.")
                else:
                    st.error("Invalid tweet URL. Please check and try again.")
        else:
            st.info("Submit a Twitter URL to display its summary here.")

# About Us Section
st.markdown('<section id="about-us"></section>', unsafe_allow_html=True)
st.title("About EchoPulse")

# Function to encode images
@st.cache_data
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = image_to_base64("static/image.png")
img2_base64 = image_to_base64("static/image2.jpg")
img3_base64 = image_to_base64("static/image3.png")

st.markdown(
    f"""
    <div class="cards-container">
        <div class="card">
            <img src="data:image/png;base64,{img_base64}" alt="Efficient Data Analysis">
            <h3>Instant Comment Analysis</h3>
            <p>EchoPulse instantly processes comments from YouTube and Twitter to reveal what your audience is truly thinking. Our advanced AI identifies trends and sentiments, giving you a clear view of user feedback without the manual effort.</p>
        </div>
        <div class="card">
            <img src="data:image/jpeg;base64,{img2_base64}" alt="User-Friendly Design">
            <h3>Intuitive & Clean Interface</h3>
            <p>We designed EchoPulse to be simple and powerful. The clean interface allows you to get the insights you need quickly, making complex data analysis accessible to everyone, from creators to marketers.</p>
        </div>
        <div class="card">
            <img src="data:image/png;base64,{img3_base64}" alt="AI-Powered Summaries">
            <h3>Smart Summaries, Not Noise</h3>
            <p>Stop scrolling through endless comments. EchoPulse uses cutting-edge AI to condense thousands of comments into concise, actionable summaries. Understand the key themes and overall sentiment in seconds.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Contact Us Section
st.markdown('<section id="contact-us"></section>', unsafe_allow_html=True)
st.title("Contact Us")

def send_email(name, sender_email, message):
    try:
        # --- IMPORTANT ---
        # 1. Replace the password with YOUR OWN 16-character Google App Password.
        # 2. For better security, store these in Streamlit Secrets (st.secrets).
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email_address = "dharanimurugaraj@gmail.com"  # YOUR EMAIL
        sender_email_password = "xjwobumtdbxsbkpu" # YOUR APP PASSWORD

        # The recipient email is also your email
        recipient_email = "dharanimurugaraj@gmail.com"

        # Create email content
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message}"
        
        msg = MIMEMultipart()
        msg["From"] = sender_email_address
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email_address, sender_email_password)
        server.sendmail(sender_email_address, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

with st.container():
    col1, col2 = st.columns([1,2])
    with col2:
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Your Message", height=150)
            submit_contact = st.form_submit_button("Send Message")

            if submit_contact:
                if name and email and message:
                    if send_email(name, email, message):
                        st.success("Your message has been sent successfully!")
                    else:
                        st.error("Failed to send your message. Please try again later.")
                else:
                    st.warning("Please fill out all fields before sending.")

# Footer
st.markdown(
    """
    <footer>
        <p>&copy; 2025 EchoPulse. All rights reserved.</p>
    </footer>
    """,
    unsafe_allow_html=True,
)
