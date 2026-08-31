import asyncio
from typing import List
from models import UserAnswer
from form_reader import active_sessions

async def fill_form(session_id: str, answers: List[UserAnswer]) -> dict:
    if session_id not in active_sessions:
        raise ValueError("Invalid or expired session.")
        
    session = active_sessions[session_id]
    page = session["page"]
    listitems = session["listitems"]
    
    # We will map answers by matching question text, or we can assume the index 
    # of listitems corresponds to the order of questions extracted.
    # To be robust, let's iterate answers and find the matching listitem.
    
    for user_answer in answers:
        if user_answer.answer is None:
            continue
            
        # Find the listitem that contains this question text
        target_item = None
        for item in listitems:
            heading = await item.query_selector('div[role="heading"]')
            if heading:
                text = await heading.inner_text()
                # Clean text like in reader
                text = text.replace("*", "").strip()
                if text == user_answer.question:
                    target_item = item
                    break
                    
        if not target_item:
            print(f"Could not find DOM element for question: {user_answer.question}")
            continue
            
        try:
            # Fill based on type
            # We don't have the explicit type stored in target_item, but we can detect it again
            # or just try filling different inputs.
            
            # Short answer / Paragraph
            text_input = await target_item.query_selector('input[type="text"]')
            if text_input:
                await text_input.fill(str(user_answer.answer))
                continue
                
            textarea = await target_item.query_selector('textarea')
            if textarea:
                await textarea.fill(str(user_answer.answer))
                continue
                
            # Multiple Choice (Radio)
            radios = await target_item.query_selector_all('div[role="radio"]')
            if radios:
                for r in radios:
                    data_val = await r.get_attribute('data-value')
                    if data_val == str(user_answer.answer):
                        await r.click()
                        break
                continue
                
            # Checkbox
            checkboxes = await target_item.query_selector_all('div[role="checkbox"]')
            if checkboxes:
                ans_list = user_answer.answer if isinstance(user_answer.answer, list) else [user_answer.answer]
                for c in checkboxes:
                    data_val = await c.get_attribute('data-value')
                    if data_val in ans_list:
                        # check if already checked (aria-checked="true")
                        is_checked = await c.get_attribute('aria-checked')
                        if is_checked != "true":
                            await c.click()
                continue
                
            # Dropdown
            listbox = await target_item.query_selector('div[role="listbox"]')
            if listbox:
                await listbox.click()
                await page.wait_for_timeout(500)
                # Find option with exact text
                options = await page.query_selector_all('div[role="option"]')
                for opt in options:
                    text = await opt.inner_text()
                    if text == str(user_answer.answer):
                        await opt.click()
                        break
                continue
                
            # Date
            date_input = await target_item.query_selector('input[type="date"]')
            if date_input:
                await date_input.fill(str(user_answer.answer))
                continue
                
            # Fallback for short answer
            fallback_input = await target_item.query_selector('input')
            if fallback_input:
                await fallback_input.fill(str(user_answer.answer))
                
        except Exception as e:
            print(f"Error filling question '{user_answer.question}': {e}")

    # DO NOT CLICK SUBMIT as per requirements.
    # User will review the form.
    # We should take a screenshot or just return success and keep the browser open.
    # In a real desktop app, we'd bring the browser to front. 
    # For this backend, we return success and the user can check the browser window.
    # Since headless=True might be set, the user can't see it. Let's make sure headless=False is an option.
    
    return {"status": "filled", "session_id": session_id}
