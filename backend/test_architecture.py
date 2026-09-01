import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from form_reader import extract_form_data, close_session
from agent import decide_answers
from url_generator import generate_prefilled_url

async def run_test():
    url = "https://docs.google.com/forms/d/e/1FAIpQLSfiT6dO-w2Fv84m5U-9JzDMyUj20o_T_G4R4T3A3pWwKj-sLw/viewform"
    print("1. Extracting data...")
    res = await extract_form_data(url)
    print("Questions found:", len(res["questions"]))
    
    # Just close the session as we don't need it
    await close_session(res["session_id"])
    
    print("2. Matching answers...")
    # Mocking FormQuestion object list from dicts
    from models import FormQuestion
    q_objs = [FormQuestion(**q) for q in res["questions"]]
    decisions = await decide_answers(q_objs)
    
    for d in decisions:
        print(f"{d.question} -> Fill: {d.fill}, Ans: {d.answer}, ID: {next((q.entry_id for q in q_objs if q.question == d.question), None)}")
    
    print("3. Generating URL...")
    final_url = generate_prefilled_url(url, q_objs, decisions)
    print("Final URL:")
    print(final_url)

asyncio.run(run_test())
