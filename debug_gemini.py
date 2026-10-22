import asyncio
import os
import sys
import json

# Add current dir to path
sys.path.append(os.getcwd())

from app.services.gemini_search_assistant import GeminiSearchAssistant

async def test_enrichment():
    assistant = GeminiSearchAssistant()
    query = "bukhari"
    print(f"Testing query: {query}")
    
    res, err = await assistant.process_query(query)
    if err:
        print(f"Error: {err}")
    else:
        print("Gemini Result:")
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_enrichment())
