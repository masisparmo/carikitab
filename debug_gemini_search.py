import os
import asyncio
import google.generativeai as genai
import json

# Setup API Key
API_KEY = os.environ.get("GEMINI_API_KEY") # Ensure this is set in your env
if not API_KEY:
    # Try alternate keys
    for i in range(1, 10):
        if os.environ.get(f"GEMINI_API_KEY_{i}"):
            API_KEY = os.environ.get(f"GEMINI_API_KEY_{i}")
            break

genai.configure(api_key=API_KEY)

async def test_gemini_search(keyword):
    print(f"Asking Gemini to search for: {keyword}")
    model = genai.GenerativeModel('gemini-2.0-flash') # Using 2.0 or 1.5
    
    # We ask Gemini to search the web and find specific links
    prompt = f"""
    Search Google or Shamela.org to find PDF book links for the keyword: "{keyword}".
    Focus ONLY on results from 'shamela.org/pdf' or 'shamela.org/books'.
    
    Return the result strictly as a JSON array of objects:
    [
      {{"title": "Book Title", "author": "Author Name", "url": "https://shamela.org/pdf/..."}},
      ...
    ]
    Limit to 10 results. No other text.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean JSON structure
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        
        results = json.loads(text)
        print(f"Gemini found {len(results)} books.")
        for i, b in enumerate(results[:5]):
            print(f"{i+1}. {b['title']} by {b['author']} -> {b['url']}")
        return results
    except Exception as e:
        print(f"Gemini Search Error: {e}")
        return []

if __name__ == "__main__":
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in environment.")
    else:
        asyncio.run(test_gemini_search("shahih bukhari"))
