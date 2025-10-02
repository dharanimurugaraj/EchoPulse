import streamlit as st
import tweepy
import re
from dotenv import load_dotenv

# Load environment variables (Ensure .env file contains the secrets)
load_dotenv()

# Load API keys from secrets (should be in the Streamlit secrets)
twitter_api_key = st.secrets["TWITTER_API_KEY"]
twitter_api_secret = st.secrets["TWITTER_API_KEY_SECRET"]
twitter_access_token = st.secrets["TWITTER_ACCESS_TOKEN"]
twitter_access_secret = st.secrets["TWITTER_ACCESS_TOKEN_SECRET"]
twitter_bearer = st.secrets["TWITTER_BEARER_TOKEN"]

# Use Tweepy's Client for API v2 (OAuth 2.0 Bearer Token)
def initialize_twitter_client_v2():
    """Initialize the Twitter API client using Tweepy (API v2)."""
    client = tweepy.Client(bearer_token=twitter_bearer)
    return client

def extract_tweet_id_from_url(tweet_url):
    """Extract the Tweet ID from the provided URL."""
    match = re.search(r"status/(\d+)", tweet_url)
    if match:
        return match.group(1)
    else:
        st.error("Invalid tweet URL. Please provide a valid URL.")
        return None

def fetch_tweet_replies(client, tweet_id, max_replies=100):
    """Fetch replies to a specific tweet using the Twitter API v2."""
    try:
        replies = []
        
        # Fetch the original tweet to get its conversation_id
        original_tweet = client.get_tweet(tweet_id, tweet_fields=["conversation_id"])
        
        if not original_tweet.data:
            st.error("Could not find the original tweet.")
            return None
        
        conversation_id = original_tweet.data.get("conversation_id")
        
        # Search for replies using the conversation_id
        query = f"conversation_id:{conversation_id} is:reply"
        
        # Fetch replies
        response = client.search_recent_tweets(
            query=query,
            tweet_fields=["author_id", "created_at", "text"],
            max_results=max_replies
        )
        
        if response.data:
            for tweet in response.data:
                replies.append(tweet.text)
        
        return replies
    
    except tweepy.TweepyException as e:
        st.error(f"Error fetching replies: {e}")
        return None

def load_replies_in_format(replies):
    """Aggregate replies into a single formatted string."""
    formatted_replies = "\n".join(replies) if replies else "No replies found."
    return formatted_replies


def categorize_replies(replies):
    """Categorize replies into positive, negative, and themes."""
    positive_keywords = ["good", "great", "excellent", "amazing", "awesome", "fantastic", "incredible", "wonderful", "brilliant", "outstanding", "thank", "appreciate", "grateful", "love", "admire", "respect", "support", "happy", "proud", "inspiring", "encouraging", "hopeful", "positive", "motivated", "excited", "yay", "wow", "fun", "enjoy", "laugh", "like", "thrilled", "helpful", "insightful", "informative", "useful", "educational", "clear", "simple", "effective", "innovative", "creative", "clever", "advanced", "futuristic", "revolutionary", "fast", "reliable", "responsive", "friendly", "patient", "accommodating", "healthy", "safe", "secure", "caring", "beneficial"]
    negative_keywords = ["bad", "terrible", "horrible", "awful", "poor", "worse", "worst", "hate", "dislike", "annoyed", "frustrating", "disappointing", "upset", "angry", "irritated", "sad", "sorry", "regret", "pity", "hurt", "unfortunate", "worried", "depressed", "useless", "unhelpful", "unnecessary", "pointless", "boring", "irrelevant", "problem", "issue", "fail", "failure", "broken", "wrong", "misleading", "unclear", "mistake", "unsafe", "harmful", "side effects", "risky", "not effective", "slow", "lag", "crash", "error", "bug", "glitch", "outdated", "incompatible", "rude", "unresponsive", "long wait", "unresolved", "unprofessional"]
    themes = {}
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

    for reply in replies:
        sentiment = "neutral"
        for word in positive_keywords:
            if word in reply.lower():
                sentiment = "positive"
                sentiment_counts["positive"] += 1
                break
        for word in negative_keywords:
            if word in reply.lower():
                sentiment = "negative"
                sentiment_counts["negative"] += 1
                break

        if sentiment == "neutral":
            sentiment_counts["neutral"] += 1

        # Extract themes (basic keyword extraction for demonstration)
        for word in reply.lower().split():
            themes[word] = themes.get(word, 0) + 1

    sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]  # Top 5 themes
    return {"positive": sentiment_counts["positive"], "negative": sentiment_counts["negative"], "neutral": sentiment_counts["neutral"], "themes": sorted_themes}

def summarize_replies(replies):
    """Generate a descriptive summary of the comments."""
    if not replies:
        return "No replies to summarize."

    analysis = categorize_replies(replies)

    # Create a narrative description based on the analysis
    summary = "The overall tone of the comments appears "
    
    # Determine the overall sentiment
    if analysis["positive"] > analysis["negative"]:
        summary += "The sentiment is largely positive, with many replies appreciating the content or providing supportive feedback. A significant number of commenters expressed admiration and approval for the subject matter, highlighting aspects they found impressive or inspiring. Users have praised the post for its quality, clarity, or overall impact, and many have left encouraging comments, showing their satisfaction and encouraging others to engage with the content. There’s a clear sense of appreciation and positivity toward the content, with users expressing their excitement and support. "
    elif analysis["negative"] > analysis["positive"]:
        summary += "The sentiment is mostly critical, with concerns or negative opinions raised by several commenters. A large portion of replies conveyed dissatisfaction or disagreement with the content, raising issues or concerns related to its accuracy, approach, or implications. Commenters have voiced frustration, disappointment, or even anger, criticizing certain aspects or expressing doubts about the validity or relevance of the content. This critical feedback often suggests areas for improvement or calls for further clarification, reflecting a negative overall sentiment from the majority of the replies. "
    else:
        summary += "The sentiment is mixed, with both supportive and critical viewpoints equally expressed. The replies exhibit a blend of approval and disapproval, where users both praise and criticize the content. Some commenters have expressed positive opinions, highlighting what they liked or appreciated, while others have raised concerns or pointed out flaws. This balance of sentiments creates a diverse conversation, where users share different perspectives and engage in debates, with both constructive feedback and critiques. It reflects a situation where the content has sparked a wide range of reactions, from admiration to skepticism or disagreement "

    # Highlight the key themes (in this case, usernames mentioned)
    key_usernames = [theme[0] for theme in analysis["themes"] if theme[0].startswith('@')]  # Assuming usernames start with '@'
    
    if key_usernames:
        summary += f"The main topics of discussion include: {', '.join(key_usernames)}."

    return summary