import asyncio
import uuid
import os
from playwright.async_api import async_playwright, Page
from models import FormQuestion, FormAnalysisResponse

# Global dictionary to store active Playwright sessions (pages)
# In a real app, we'd use a more robust session manager.
active_sessions = {}
browsers = {}

async def init_browser():
    playwright = await async_playwright().start()
    is_headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = await playwright.chromium.launch(headless=is_headless)
    return playwright, browser

async def extract_form_data(url: str) -> dict:
    playwright = await async_playwright().start()
    is_headless = os.getenv("HEADLESS", "true").lower() == "true"
    browser = await playwright.chromium.launch(headless=is_headless)
    context = await browser.new_context()
    page = await context.new_page()
    
    await page.goto(url, wait_until="domcontentloaded")
    # Wait for the main form content to render
    try:
        await page.wait_for_selector('div[role="listitem"]', timeout=5000)
    except:
        print("DEBUG: Timeout waiting for listitem selector.")
    
    await page.wait_for_timeout(3000)
    
    # ------------------- DIAGNOSTICS -------------------
    print("DEBUG: Final URL ->", page.url)
    print("DEBUG: Page Title ->", await page.title())
    
    html = await page.content()
    with open("debug_form.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("DEBUG: Saved debug_form.html")
    
    await page.screenshot(path="debug_form.png", full_page=True)
    print("DEBUG: Saved debug_form.png")
    
    listitems_count = len(await page.query_selector_all('div[role="listitem"]'))
    input_count = len(await page.query_selector_all('input'))
    radio_count = len(await page.query_selector_all('[role="radio"]'))
    listbox_count = len(await page.query_selector_all('[role="listbox"]'))
    
    print(f"DEBUG: [role='listitem'] count -> {listitems_count}")
    print(f"DEBUG: input count -> {input_count}")
    print(f"DEBUG: [role='radio'] count -> {radio_count}")
    print(f"DEBUG: [role='listbox'] count -> {listbox_count}")
    # ---------------------------------------------------
    
    # Extract title
    title_element = await page.query_selector('div[role="heading"][aria-level="1"]')
    title = await title_element.inner_text() if title_element else "Google Form"
    
    # Extract questions
    questions = []
    
    listitems = await page.query_selector_all('div[role="listitem"]')
    
    for idx, item in enumerate(listitems):
        try:
            # Question title is usually in a role="heading" inside the listitem
            heading_el = await item.query_selector('div[role="heading"]')
            if not heading_el:
                continue
            question_text_full = await heading_el.inner_text()
            
            # Remove the * for required fields from text
            is_required = "*" in question_text_full
            question_text = question_text_full.replace("*", "").strip()
            
            # Determine type and options
            q_type = "unknown"
            options = []
            entry_id = None
            
            # Extract entry_id from data-params on the listitem or its child
            # data-params looks like: %.[12345,"Question",null,0,[[67890,null,1]]]
            # The entry ID is 67890 (the first number in the nested array)
            import re
            
            # Try getting data-params directly on the listitem or inner jsmodel div
            data_params = await item.get_attribute("data-params")
            if not data_params:
                jsmodel_div = await item.query_selector('div[jsmodel]')
                if jsmodel_div:
                    data_params = await jsmodel_div.get_attribute("data-params")
            
            if data_params:
                # Regex to find the entry ID inside the nested array structure [[<id>,
                match = re.search(r'\[\[(\d+),', data_params)
                if match:
                    entry_id = match.group(1)
            
            # Fallback if data-params extraction fails: check inputs directly
            if not entry_id:
                hidden_input = await item.query_selector('input[name^="entry."]')
                if hidden_input:
                    name_attr = await hidden_input.get_attribute("name")
                    if name_attr and name_attr.startswith("entry."):
                        entry_id = name_attr.split(".")[1]
                else:
                    any_input = await item.query_selector('[name^="entry."]')
                    if any_input:
                        name_attr = await any_input.get_attribute("name")
                        if name_attr and name_attr.startswith("entry."):
                            entry_id = name_attr.split(".")[1]
            
            # Check for radio (multiple_choice)
            radios = await item.query_selector_all('div[role="radio"]')
            if radios:
                q_type = "multiple_choice"
                for r in radios:
                    data_value = await r.get_attribute('data-value')
                    if data_value:
                        options.append(data_value)
            
            # Check for checkboxes
            checkboxes = await item.query_selector_all('div[role="checkbox"]')
            if checkboxes:
                q_type = "checkbox"
                for c in checkboxes:
                    data_value = await c.get_attribute('data-value')
                    if data_value:
                         options.append(data_value)
            
            # Check for dropdown (listbox)
            listbox = await item.query_selector('div[role="listbox"]')
            if listbox:
                q_type = "dropdown"
                # To get options, we might need to click it, but Google Forms sometimes 
                # renders options inside the DOM if we look closely, or we can look for
                # role="option" within the page after click. For simplicity in reader, 
                # we can find elements with role="option" within this container.
                # Actually, the options are in a separate overlay. Let's try to extract from JS data
                # Google forms puts all data in a script tag.
                # Let's fallback to clicking the dropdown to read options if needed, but for MVP:
                await listbox.click()
                await page.wait_for_timeout(500) # wait for animation
                dropdown_options = await page.query_selector_all('div[role="option"]')
                for opt in dropdown_options:
                    text = await opt.inner_text()
                    if text and text != "Choose":
                        options.append(text)
                # Click title to close dropdown
                if heading_el:
                    await heading_el.click()
            
            # Check for text inputs
            text_input = await item.query_selector('input[type="text"]')
            if text_input:
                q_type = "short_answer"
                
            textarea = await item.query_selector('textarea')
            if textarea:
                q_type = "paragraph"
                
            # Date
            date_input = await item.query_selector('input[type="date"]')
            if date_input:
                q_type = "date"
                
            if q_type == "unknown":
                # Fallback heuristics
                text_input_fallback = await item.query_selector('input')
                if text_input_fallback:
                    q_type = "short_answer"
                
            q_id = f"q_{idx}"
            
            questions.append({
                "id": q_id,
                "question": question_text,
                "type": q_type,
                "required": is_required,
                "options": options if options else None,
                "entry_id": entry_id
            })
            
        except Exception as e:
            print(f"Error extracting question: {e}")
            
    # Keep session open for filling
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "playwright": playwright,
        "browser": browser,
        "context": context,
        "page": page,
        "url": url,
        "listitems": listitems # caching list items for filling
    }
    
    return {
        "form_title": title,
        "questions": questions,
        "session_id": session_id
    }

async def close_session(session_id: str):
    if session_id in active_sessions:
        session = active_sessions[session_id]
        await session["browser"].close()
        await session["playwright"].stop()
        del active_sessions[session_id]
