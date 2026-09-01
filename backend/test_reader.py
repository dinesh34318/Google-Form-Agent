import asyncio
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from form_reader import extract_form_data

async def run_test():
    url = "https://docs.google.com/forms/d/e/1FAIpQLScJp7wEaMvH-iKuvNixB2b25N_VwK9C6bC2B8zKxYq9rD-Pmw/viewform"
    res = await extract_form_data(url)
    print("Form Title:", res["form_title"])
    for q in res["questions"]:
        print(f"Q: {q['question']} | Type: {q['type']} | Entry ID: {q.get('entry_id')} | Required: {q['required']}")

asyncio.run(run_test())
