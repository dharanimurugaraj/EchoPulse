import google.generativeai as genai
import os
import streamlit as st

# --- IMPORTANT ---
# Make sure your GEMINI_API_KEY is in your .streamlit/secrets.toml file
# GEMINI_API_KEY = "YOUR_KEY_HERE"

try:
    # Load the API key from Streamlit secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    
    genai.configure(api_key=api_key)

    print("Successfully configured the Gemini API key.")
    print("-" * 30)

    print("Listing available models...")
    # This loop will print all the models your API key has access to
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

    print("-" * 30)
    print("Attempting to initialize the 'gemini-pro' model...")
    
    # Attempt to create the model instance
    model = genai.GenerativeModel('gemini-pro-latest')
    
    print("Successfully initialized the model.")
    print("Attempting to generate content...")

    # Send a simple prompt
    response = model.generate_content("Tell me a fun fact about the ocean.")
    
    print("SUCCESS! Response received:")
    print(response.text)

except Exception as e:
    print("\n--- AN ERROR OCCURRED ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    print("\n--- TROUBLESHOOTING ---")
    print("1. API Key Check: Double-check if the GEMINI_API_KEY in your secrets.toml file is 100% correct.")
    print("2. API Enabled Check: Ensure the 'Generative Language API' is ENABLED in your Google Cloud project.")
    print("3. Billing Check: Make sure your Google Cloud project is linked to an active and valid billing account.")