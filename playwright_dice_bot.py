#!/usr/bin/env python3
import asyncio
import os
import time
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# For AI-based cover letter generation
import openai
from fpdf import FPDF
from unidecode import unidecode

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/dice_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Check for required env variables
required_vars = ['DICE_EMAIL', 'DICE_PASSWORD']
for var in required_vars:
    if not os.environ.get(var):
        logger.error(f"Missing required environment variable: {var}")
        sys.exit(1)

# Constants
DICE_EMAIL = os.environ.get('DICE_EMAIL')
DICE_PASSWORD = os.environ.get('DICE_PASSWORD')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
USE_AI = bool(OPENAI_API_KEY)

# Resume paths
resources_path = Path('app/resources')
RESUME_PATH = str((resources_path / 'resume.pdf').resolve())
COVER_LETTER_PATH = str((resources_path / 'cover_letter.pdf').resolve())

# Search parameters (from settings.py)
SEARCH_QUERY = "QA Automation Engineer Test Architect Playwright Cypress Selenium AI"
LOCATION_QUERY = "New York"
REMOTE_ONLY = True
EASY_APPLY_ONLY = True
DAYS_AGO = 7  # Last 7 days

class DiceBot:
    """Playwright-based bot for automating job applications on Dice.com"""
    
    def __init__(self):
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY) if USE_AI else None
        
        # For resume content
        try:
            # Import fitz (PyMuPDF) with proper error handling
            try:
                import fitz  # PyMuPDF is imported as fitz
                doc = fitz.open(RESUME_PATH)
                self.resume_text = "\n".join([page.get_text() for page in doc])
                logger.info("Resume loaded successfully")
            except ImportError:
                logger.warning("PyMuPDF not installed correctly. Installing now...")
                os.system("pip3 install PyMuPDF")
                import fitz
                doc = fitz.open(RESUME_PATH)
                self.resume_text = "\n".join([page.get_text() for page in doc])
                logger.info("Resume loaded successfully after installing PyMuPDF")
        except Exception as e:
            logger.error(f"Error loading resume: {e}")
            self.resume_text = ""
    
    async def write_cover_letter(self, job_description):
        """Generate a cover letter using OpenAI and save as PDF"""
        logger.info("Generating cover letter with AI...")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Please write a short cover letter using the information from the provided "
                                            "resume and job description. Please skip identifying information as it will "
                                            "already be included in the resume. "
                                            f"The resume follows here: \n'''\n{self.resume_text}\n'''"},
                {"role": "user", "content": f"The job description is the following: \n'''\n{job_description}\n'''"}
            ]
        )

        cover_letter_text = unidecode(response.choices[0].message.content)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=12)
        pdf.multi_cell(0, 10, cover_letter_text)
        
        # Save PDF
        if os.path.exists(COVER_LETTER_PATH):
            os.remove(COVER_LETTER_PATH)
        pdf.output(COVER_LETTER_PATH)
        logger.info(f"Cover letter saved to {COVER_LETTER_PATH}")
    
    async def run(self):
        """Main method to run the bot"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)  # Set to True for production
            self.context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await self.context.new_page()
            
            try:
                # Login to Dice
                await self.login(page)
                
                # Search for jobs
                await self.search_jobs(page)
                
                # Apply filters
                await self.apply_filters(page)
                
                # Process job listings
                await self.process_job_listings(page)
                
            except Exception as e:
                logger.error(f"Error: {e}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                # Close browser
                await browser.close()
    
    async def login(self, page):
        """Login to Dice.com"""
        logger.info("Logging into Dice.com...")
        
        # Navigate to login page
        await page.goto("https://www.dice.com/dashboard/login")
        
        # Two-step login: first email then password
        logger.info("Entering email...")
        await page.wait_for_selector('input[name="email"]')
        await page.fill('input[name="email"]', DICE_EMAIL)
        await page.click('button[type="submit"]')
        
        # Wait for password field
        logger.info("Entering password...")
        await page.wait_for_selector('input[name="password"]', timeout=10000)
        await page.fill('input[name="password"]', DICE_PASSWORD)
        await page.click('button[type="submit"]')
        
        # Wait for home feed to load (updated from dashboard to home-feed)
        logger.info("Waiting for login to complete...")
        try:
            # Try multiple possible URL patterns
            for pattern in ["**/home-feed*", "**/dashboard*", "**/jobs*"]:
                try:
                    await page.wait_for_url(pattern, timeout=5000)
                    logger.info(f"Login successful, navigated to URL matching: {pattern}")
                    return  # Exit method if any URL pattern matches
                except PlaywrightTimeoutError:
                    continue
            
            # If we get here, none of the URL patterns matched within timeout
            # Just wait for navigation to complete and check if login was successful
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check if we're logged in by looking for common elements
            for selector in ['[data-cy="profile-menu"]', '.user-menu', '[aria-label="User menu"]', 'a[href*="profile"]']:
                if await page.locator(selector).count() > 0:
                    logger.info(f"Login confirmed by finding element: {selector}")
                    return
                    
            # If we get here, we couldn't confirm login
            current_url = page.url
            logger.warning(f"Couldn't confirm login success. Current URL: {current_url}")
            # Take screenshot for debugging
            await page.screenshot(path="logs/login_result.png")
            # Continue anyway
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            # Continue anyway - the search might still work
    
    async def search_jobs(self, page):
        """Search for jobs using configured parameters"""
        logger.info(f"Searching for jobs: {SEARCH_QUERY} in {LOCATION_QUERY}")
        
        # Try to navigate directly to job search page first
        try:
            # Try different possible URLs for job search
            for search_url in ["https://www.dice.com/jobs", "https://www.dice.com/platform/jobs"]:
                try:
                    await page.goto(search_url)
                    await page.wait_for_load_state("networkidle")
                    logger.info(f"Navigated directly to jobs page: {search_url}")
                    break
                except Exception as e:
                    logger.warning(f"Navigation to {search_url} failed: {e}")
        except Exception as e:
            logger.warning(f"Direct navigation to jobs page failed: {e}")
            # Continue with original approach through UI
        
        # Take screenshot to see the current state
        await page.screenshot(path="logs/search_page_initial.png")
        logger.info(f"Current URL before search: {page.url}")
        
        # Wait a bit for page to stabilize
        await page.wait_for_timeout(2000)
        
        # Find and fill search fields - try multiple selector options
        search_found = False
        for selector in [
            'input[name="q"]', 
            '#typeaheadInput', 
            'input[placeholder*="job title"]', 
            'input[placeholder*="skill"]', 
            '[data-cy="search-field-keyword"]',
            'input[type="search"]'
        ]:
            try:
                if await page.locator(selector).count() > 0:
                    # Clear first in case there's existing text
                    await page.locator(selector).fill("")
                    await page.wait_for_timeout(300)
                    await page.locator(selector).fill(SEARCH_QUERY)
                    logger.info(f"Found and filled search input with selector: {selector}")
                    search_found = True
                    break
            except Exception as e:
                logger.warning(f"Error with search input selector {selector}: {e}")
        
        if not search_found:
            logger.warning("Could not find search input - taking screenshot for debugging")
            await page.screenshot(path="logs/search_input_not_found.png")
        
        # Similar improvements for location field...
        location_found = False
        for selector in [
            'input[name="location"]', 
            '#google-location-search', 
            'input[placeholder*="location"]', 
            '[data-cy="search-field-location"]',
            'input[placeholder="Location"]'
        ]:
            try:
                if await page.locator(selector).count() > 0:
                    # Clear first
                    await page.locator(selector).fill("")
                    await page.wait_for_timeout(300)
                    await page.locator(selector).fill(LOCATION_QUERY)
                    logger.info(f"Found and filled location input with selector: {selector}")
                    location_found = True
                    break
            except Exception as e:
                logger.warning(f"Error with location input selector {selector}: {e}")
        
        if not location_found:
            logger.warning("Could not find location input - taking screenshot for debugging")
            await page.screenshot(path="logs/location_input_not_found.png")

        # Wait a bit before clicking search
        await page.wait_for_timeout(1000)
        
        # Click search button
        search_button_found = False
        for selector in [
            'button[type="submit"]', 
            'button:has-text("Search")', 
            '[data-cy="search-button"]', 
            '.search-button',
            'button.btn-primary'
        ]:
            try:
                button = page.locator(selector).first
                if await button.count() > 0:
                    logger.info(f"Found search button with selector: {selector}")
                    await button.click()
                    search_button_found = True
                    break
            except Exception as e:
                logger.warning(f"Error with search button selector {selector}: {e}")
        
        if not search_button_found:
            logger.warning("Could not find search button - taking screenshot for debugging")
            await page.screenshot(path="logs/search_button_not_found.png")
            # Try pressing Enter key as fallback
            logger.info("Trying to press Enter key as fallback")
            await page.keyboard.press("Enter")
        
        # Wait longer for search results to load
        try:
            await page.wait_for_url("**/jobs*", timeout=30000)
            logger.info("Search completed, URL contains /jobs")
        except PlaywrightTimeoutError:
            logger.warning("Timeout waiting for /jobs URL pattern")
            # Continue anyway, check page content to confirm search results
        
        # Wait for network activity to settle
        await page.wait_for_load_state("networkidle", timeout=30000)
        await page.wait_for_timeout(5000)  # Additional wait to ensure results load
        
        # Take screenshot after search
        await page.screenshot(path="logs/after_search.png")
        
        # More comprehensive verification of search results
        job_found = False
        for selector in [
            '[data-cy="search-card"]', 
            '.job-card', 
            '.search-result-item', 
            'article',
            '[data-cy*="job"]',
            '.dhi-search-cards'
        ]:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    logger.info(f"Found {count} search results with selector: {selector}")
                    job_found = True
                    break
            except Exception as e:
                logger.warning(f"Error checking for search results with selector {selector}: {e}")
        
        if not job_found:
            logger.warning("Could not find job cards after search - taking screenshot")
            await page.screenshot(path="logs/search_results_not_found.png")
    
    async def apply_filters(self, page):
        """Apply filters for date posted, remote, easy apply"""
        logger.info("Applying filters...")
        
        # Take screenshot before applying filters
        await page.screenshot(path="logs/before_filters.png")
        
        # More robust filter application with retry logic
        async def try_apply_filter(filter_name, selectors, value_selectors=None):
            """Helper to try multiple selectors for a filter"""
            logger.info(f"Attempting to apply {filter_name} filter")
            
            for attempt in range(3):  # Try up to 3 times
                try:
                    # Find and click the filter dropdown/button
                    for selector in selectors:
                        filter_elem = page.locator(selector).first
                        if await filter_elem.count() > 0:
                            logger.info(f"Found {filter_name} filter with selector: {selector}")
                            await filter_elem.click()
                            await page.wait_for_timeout(500)  # Short wait for dropdown
                            
                            # If it's a dropdown with value options
                            if value_selectors:
                                value_found = False
                                for value_selector in value_selectors:
                                    value_elem = page.locator(value_selector).first
                                    if await value_elem.count() > 0:
                                        logger.info(f"Found value option with selector: {value_selector}")
                                        await value_elem.click()
                                        value_found = True
                                        break
                                
                                if not value_found:
                                    logger.warning(f"Could not find value option for {filter_name}")
                                    # Close dropdown by pressing Escape
                                    await page.keyboard.press("Escape")
                            
                            # Wait for filters to apply
                            await page.wait_for_timeout(1000)
                            return True
                    
                    # If we get here, we didn't find the filter in this attempt
                    logger.warning(f"Attempt {attempt+1}: Could not find {filter_name} filter")
                    await page.wait_for_timeout(1000)  # Wait before retry
                    
                except Exception as e:
                    logger.warning(f"Error applying {filter_name} filter (attempt {attempt+1}): {e}")
                    await page.wait_for_timeout(1000)  # Wait before retry
            
            # If we get here, all attempts failed
            logger.error(f"Failed to apply {filter_name} filter after multiple attempts")
            return False
        
        # Date posted filter
        date_filter_selectors = [
            'button:has-text("Date Posted")', 
            '[aria-label="Date Posted filter"]',
            '[data-cy="search-filters-date-posted"]',
            '#datePosted-filter'
        ]
        date_value_selectors = [
            'text="Last 7 days"',
            '[value="7"]',
            '[data-cy="search-filters-datePosted-7"]',
            '[data-value="7"]'
        ]
        await try_apply_filter("Date Posted", date_filter_selectors, date_value_selectors)
        
        # Remote filter
        if REMOTE_ONLY:
            remote_selectors = [
                'button:has-text("Remote")',
                '[aria-label*="Remote"]',
                '[data-cy="search-filters-remote"]',
                '#remote-filter',
                'label:has-text("Remote")'
            ]
            await try_apply_filter("Remote", remote_selectors)
        
        # Easy Apply filter
        if EASY_APPLY_ONLY:
            easy_apply_selectors = [
                'text="Easy Apply"',
                '[aria-label*="Easy Apply"]',
                '[data-cy="search-filters-easyApply"]',
                '#easy-apply-filter',
                'label:has-text("Easy Apply")'
            ]
            await try_apply_filter("Easy Apply", easy_apply_selectors)
        
        # Take screenshot after applying filters
        await page.screenshot(path="logs/after_filters.png")
        
        # Wait for results to update after filters
        await page.wait_for_timeout(3000)
        
        # Check if filters were applied by looking for filter pills/tags
        try:
            filter_pills = await page.locator('.filter-pill, [data-cy="search-filter-pill"]').all()
            pill_count = len(filter_pills)
            if pill_count > 0:
                logger.info(f"Found {pill_count} active filter pills, filters appear to be applied")
            else:
                logger.warning("No filter pills found, filters may not have been applied")
        except Exception as e:
            logger.warning(f"Error checking filter pills: {e}")
    
    async def process_job_listings(self, page):
        """Process all job listings that match our criteria"""
        logger.info("Processing job listings...")
        
        # Take a screenshot of the search results
        await page.screenshot(path="logs/search_results.png")
        
        # Get the total number of jobs found
        try:
            count_elements = [
                '[data-cy="search-count-header"]',
                '.search-count',
                'h1:has-text("jobs")'
            ]
            
            for selector in count_elements:
                count_elem = page.locator(selector).first
                if await count_elem.count() > 0:
                    count_text = await count_elem.text()
                    logger.info(f"Found jobs count element: {count_text}")
                    break
        except Exception:
            logger.info("Couldn't find job count element")
        
        # Process jobs on the current page
        page_num = 1
        total_applied = 0
        max_applications = 20  # Safety limit
        
        while True and total_applied < max_applications:
            logger.info(f"Processing page {page_num}")
            
            # Get all job cards on the page - try multiple possible selectors
            job_cards = None
            for selector in ['[data-cy="search-card"]', '.job-card', '.search-result-item', 'article']:
                cards = page.locator(selector)
                count = await cards.count()
                if count > 0:
                    logger.info(f"Found {count} job cards with selector: {selector}")
                    job_cards = cards
                    break
            
            if not job_cards or await job_cards.count() == 0:
                logger.info("No jobs found on this page")
                await page.screenshot(path=f"logs/no_jobs_page_{page_num}.png")
                break
            
            job_count = await job_cards.count()
            logger.info(f"Found {job_count} jobs on page {page_num}")
            
            # Process each job
            for i in range(job_count):
                if total_applied >= max_applications:
                    logger.info(f"Reached maximum applications limit ({max_applications})")
                    break
                    
                try:
                    # Get the job card (refresh to avoid stale references)
                    job_cards_refreshed = job_cards
                    if await job_cards_refreshed.count() <= i:
                        logger.warning(f"Job card index {i} no longer available, refreshing page")
                        await page.reload()
                        await page.wait_for_load_state("networkidle")
                        for selector in ['[data-cy="search-card"]', '.job-card', '.search-result-item', 'article']:
                            cards = page.locator(selector)
                            if await cards.count() > 0:
                                job_cards_refreshed = cards
                                break
                    
                    current_card = job_cards_refreshed.nth(i)
                    
                    # Check if already applied - try different indicators
                    already_applied = False
                    for applied_selector in ['text="Applied"', '.applied-tag', '[data-cy="applied-tag"]']:
                        applied_badge = current_card.locator(applied_selector)
                        if await applied_badge.count() > 0:
                            logger.info(f"Skipping job {i+1} (already applied)")
                            already_applied = True
                            break
                    
                    if already_applied:
                        continue
                    
                    # Extract job title for logging - try different selectors
                    job_title = "Unknown Job Title"
                    for title_selector in ['[data-cy="card-title-link"]', 'h2', '.job-title', 'a[href*="/jobs/detail"]']:
                        title_elem = current_card.locator(title_selector).first
                        if await title_elem.count() > 0:
                            job_title = await title_elem.text()
                            break
                    
                    logger.info(f"Opening job {i+1}: {job_title}")
                    
                    # Take screenshot of the card before clicking
                    await current_card.screenshot(path=f"logs/job_card_{page_num}_{i}.png")
                    
                    # Click to open job details
                    await current_card.click()
                    
                    # Wait for job details page to load in a new tab
                    try:
                        new_page = await self.context.wait_for_page(timeout=10000)
                        await new_page.wait_for_load_state('networkidle')
                        
                        # Take screenshot of job details
                        await new_page.screenshot(path=f"logs/job_details_{page_num}_{i}.png")
                        
                        # Extract job details
                        job_description = ""
                        for desc_selector in ['[data-cy="job-description"]', '.job-description', '#jobDescription']:
                            desc_elem = new_page.locator(desc_selector).first
                            if await desc_elem.count() > 0:
                                job_description = await desc_elem.text()
                                logger.info(f"Found job description ({len(job_description)} chars)")
                                break
                        
                        if not job_description:
                            logger.warning("Could not find job description")
                            job_description = await new_page.locator('body').text()
                        
                        # Find apply button - try various selectors
                        apply_button = None
                        for apply_selector in [
                            'button:has-text("Apply Now")', 
                            '[data-cy="apply-button"]',
                            'a:has-text("Apply")',
                            'button:has-text("Apply")',
                            'a[href*="apply"]',
                            '.apply-button'
                        ]:
                            button = new_page.locator(apply_selector).first
                            if await button.count() > 0:
                                logger.info(f"Found apply button with selector: {apply_selector}")
                                apply_button = button
                                break
                        
                        if apply_button:
                            # Click Apply button
                            await apply_button.click()
                            await new_page.wait_for_load_state('networkidle')
                            
                            # Take screenshot after clicking apply
                            await new_page.screenshot(path=f"logs/apply_form_{page_num}_{i}.png")
                            
                            # Handle application process
                            application_result = await self.handle_application(new_page, job_description, job_title)
                            if application_result:
                                total_applied += 1
                                logger.info(f"Total jobs applied: {total_applied}/{max_applications}")
                        else:
                            logger.warning(f"No Apply button found for job: {job_title}")
                        
                        # Close the job details tab
                        await new_page.close()
                        
                    except Exception as e:
                        logger.error(f"Error processing job details: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        # Try to close any extra tabs
                        try:
                            pages = self.context.pages
                            if len(pages) > 1:
                                for extra_page in pages[1:]:
                                    await extra_page.close()
                        except:
                            pass
                
                except Exception as e:
                    logger.error(f"Error processing job {i+1}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Try to close any extra tabs and continue
                    try:
                        pages = self.context.pages
                        if len(pages) > 1:
                            for extra_page in pages[1:]:
                                await extra_page.close()
                    except:
                        pass
            
            # Check if there's a next page
            next_button_found = False
            for next_selector in ['[data-cy="pagination-next"]', '.next-page', 'a:has-text("Next")']:
                next_button = page.locator(next_selector).first
                if await next_button.count() > 0:
                    # Check if the button is disabled
                    is_disabled = await next_button.is_disabled() or 'disabled' in (await next_button.get_attribute('class') or '')
                    if not is_disabled:
                        logger.info(f"Moving to next page using selector: {next_selector}")
                        await next_button.click()
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(2000)  # Wait for next page to load
                        page_num += 1
                        next_button_found = True
                        break
            
            if not next_button_found:
                logger.info("No more pages to process or next button not found")
                break
        
        logger.info(f"Job processing complete. Applied to {total_applied} jobs.")
    
    async def handle_application(self, page, job_description, job_title):
        """Handle the actual application process"""
        logger.info(f"Applying to job: {job_title}")
        
        # Generate cover letter with AI if enabled
        if USE_AI and OPENAI_API_KEY:
            try:
                await self.write_cover_letter(job_description)
            except Exception as e:
                logger.error(f"Error generating cover letter: {e}")
        
        try:
            # Wait for application form to appear - try different selectors
            form_found = False
            for form_selector in ['form', '[data-cy="application-form"]', '.application-form', '#applicationForm']:
                try:
                    await page.wait_for_selector(form_selector, timeout=5000)
                    logger.info(f"Found application form with selector: {form_selector}")
                    form_found = True
                    break
                except PlaywrightTimeoutError:
                    continue
            
            if not form_found:
                logger.warning("Could not find application form - taking screenshot")
                await page.screenshot(path=f"logs/application_form_not_found_{job_title.replace(' ', '_')}.png")
                # Try to continue anyway
            
            # Check for resume upload
            resume_upload_found = False
            for upload_selector in [
                'input[type="file"][accept*=".pdf"]', 
                'input[type="file"][accept*="pdf"]',
                'input[type="file"]',
                '[data-cy="resume-upload"]'
            ]:
                resume_upload = page.locator(upload_selector).first
                if await resume_upload.count() > 0:
                    logger.info(f"Found resume upload with selector: {upload_selector}")
                    await resume_upload.set_input_files(RESUME_PATH)
                    logger.info("Resume uploaded")
                    resume_upload_found = True
                    break
            
            if not resume_upload_found:
                logger.warning("Could not find resume upload field - taking screenshot")
                await page.screenshot(path=f"logs/resume_upload_not_found_{job_title.replace(' ', '_')}.png")
            
            # Check for cover letter upload if we have one
            if USE_AI and OPENAI_API_KEY:
                cover_letter_found = False
                for cover_selector in [
                    'input[type="file"][accept*=".pdf"]:nth-of-type(2)',
                    'input[type="file"][name*="cover"]',
                    'input[type="file"][id*="cover"]',
                    '[data-cy="cover-letter-upload"]'
                ]:
                    cover_letter_upload = page.locator(cover_selector).first
                    if await cover_letter_upload.count() > 0:
                        logger.info(f"Found cover letter upload with selector: {cover_selector}")
                        await cover_letter_upload.set_input_files(COVER_LETTER_PATH)
                        logger.info("Cover letter uploaded")
                        cover_letter_found = True
                        break
                
                if not cover_letter_found:
                    logger.info("Could not find dedicated cover letter upload field (this is often normal)")
            
            # Look for and fill any required text fields
            required_fields = page.locator('input[required]:not([type="file"]), textarea[required]')
            required_count = await required_fields.count()
            logger.info(f"Found {required_count} required fields")
            
            for i in range(required_count):
                field = required_fields.nth(i)
                placeholder = await field.get_attribute('placeholder') or ''
                name = await field.get_attribute('name') or ''
                field_type = await field.get_attribute('type') or ''
                
                logger.info(f"Required field {i+1}: type={field_type}, name={name}, placeholder={placeholder}")
                
                if not await field.input_value():  # Only fill if empty
                    if 'name' in placeholder.lower() or 'name' in name.lower():
                        await field.fill("Juel Uddin")
                    elif 'email' in placeholder.lower() or 'email' in name.lower():
                        await field.fill(DICE_EMAIL)
                    elif 'phone' in placeholder.lower() or 'phone' in name.lower():
                        await field.fill("6463993045")
                    elif field_type == 'checkbox':
                        await field.check()
                    else:
                        await field.fill("Yes")  # Default for other required fields
            
            # Handle common radio button groups (often for yes/no questions)
            radio_groups = page.locator('input[type="radio"]').all()
            if await radio_groups.count() > 0:
                logger.info(f"Found radio buttons, trying to select positive options")
                # Try to select "Yes" for all radio groups
                # This is a heuristic - we're looking for labels containing "Yes"
                yes_radios = page.locator('label:has-text("Yes") input[type="radio"], input[type="radio"][value="yes"]')
                for i in range(await yes_radios.count()):
                    radio = yes_radios.nth(i)
                    if not await radio.is_checked():
                        await radio.check()
                        logger.info(f"Selected 'Yes' radio button {i+1}")
            
            # Submit application - try different selectors
            submit_found = False
            for submit_selector in [
                'button[type="submit"]', 
                'button:has-text("Submit")',
                'button:has-text("Apply")',
                '[data-cy="submit-application"]',
                '.submit-button'
            ]:
                submit_button = page.locator(submit_selector).first
                if await submit_button.count() > 0:
                    logger.info(f"Found submit button with selector: {submit_selector}")
                    # If the button is disabled, we might have missed something required
                    if await submit_button.is_disabled():
                        logger.warning("Submit button is disabled. Taking screenshot to troubleshoot.")
                        await page.screenshot(path=f"logs/disabled_submit_{job_title.replace(' ', '_')}.png")
                        # Continue anyway - we'll try to click it
                    
                    await submit_button.click()
                    logger.info(f"Application submitted for: {job_title}")
                    
                    # Log success
                    with open("logs/successful_applications.log", "a") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Applied to job: {job_title} at {page.url}\n")
                    
                    # Wait for confirmation
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=f"logs/application_result_{job_title.replace(' ', '_')}.png")
                    submit_found = True
                    return True
            
            if not submit_found:
                logger.warning(f"No submit button found for: {job_title}")
                await page.screenshot(path=f"logs/no_submit_{job_title.replace(' ', '_')}.png")
                return False
                
        except Exception as e:
            logger.error(f"Error during application process: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Log failure
            with open("logs/failed_applications.log", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Failed to apply to job: {job_title} at {page.url} - {str(e)}\n")
            return False

async def main():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    bot = DiceBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 