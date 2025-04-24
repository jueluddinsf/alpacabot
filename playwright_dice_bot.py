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
DICE_JOB_URL_PATTERN = "https://www.dice.com/job-detail/{}"

# Resume paths
resources_path = Path('app/resources')
RESUME_PATH = str((resources_path / 'resume.pdf').resolve())
COVER_LETTER_PATH = str((resources_path / 'cover_letter.pdf').resolve())

# Search parameters 
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
                
                # Process job listings using IntelliSearch
                await self.process_intellisearch_jobs(page)
                
            except Exception as e:
                logger.error(f"Error: {e}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                # Close browser
                await browser.close()
    
    async def login(self, page):
        """Login to Dice.com using the intellisearch URL directly"""
        logger.info("Logging into Dice.com...")
        
        # Navigate directly to the intellisearch login page
        await page.goto("https://www.dice.com/dashboard/login?redirectURL=/dashboard/intellisearch-jobs")
        
        # Enter email
        logger.info("Entering email...")
        await page.wait_for_selector('input[name="email"]')
        await page.fill('input[name="email"]', DICE_EMAIL)
        await page.click('button[type="submit"]')
        
        # Enter password
        logger.info("Entering password...")
        await page.wait_for_selector('input[name="password"]', timeout=10000)
        await page.fill('input[name="password"]', DICE_PASSWORD)
        await page.click('button[type="submit"]')
        
        # Wait for intellisearch page to load
        logger.info("Waiting for login to complete...")
        try:
            await page.wait_for_url("**/dashboard/intellisearch-jobs*", timeout=20000)
            logger.info("Login successful, navigated to intellisearch jobs page")
        except PlaywrightTimeoutError:
            logger.warning("Timeout waiting for intellisearch page")
            # Take screenshot for debugging
            await page.screenshot(path="logs/login_result.png")
            # Try to continue anyway
    
    async def process_intellisearch_jobs(self, page):
        """Process job listings from intellisearch page"""
        logger.info("Processing intellisearch job listings...")
        
        # Wait for job listings to load
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        
        # Take a screenshot of the intellisearch page
        await page.screenshot(path="logs/intellisearch_jobs.png")
        
        # Find all job listings - using the actual structure seen in screenshot
        job_selectors = [
            '[class*="card"]',
            '[data-cy="search-card"]',
            '.job-card',
            'article', 
            '[data-automation-id="jobCard"]'
        ]
        
        job_cards = None
        for selector in job_selectors:
            cards = page.locator(selector)
            count = await cards.count()
            if count > 0:
                logger.info(f"Found {count} job cards with selector: {selector}")
                job_cards = cards
                break
                
        if not job_cards:
            logger.error("No job listings found")
            return
            
        # Process each job listing
        job_count = await job_cards.count()
        total_applied = 0
        max_applications = 20  # Safety limit
        
        for i in range(job_count):
            if total_applied >= max_applications:
                logger.info(f"Reached maximum applications limit ({max_applications})")
                break
                
            try:
                current_card = job_cards.nth(i)
                
                # First check if the job is already applied
                applied_tag_found = False
                # Check for "Applied" text anywhere in the card
                try:
                    card_text = await current_card.text_content()
                    if "Applied" in card_text:
                        logger.info(f"Skipping job {i+1} - Already applied")
                        applied_tag_found = True
                except Exception as e:
                    logger.debug(f"Error getting card text: {e}")
                
                if applied_tag_found:
                    continue
                
                # Extract job title for logging
                job_title = "Unknown Job Title"
                job_id = None
                
                # Try to find job title and ID
                title_link = current_card.locator('a.card-title-link').first
                if await title_link.count() > 0:
                    job_title = await title_link.text_content()
                    job_id = await title_link.get_attribute('id')
                    logger.info(f"Found job title: {job_title} with ID: {job_id}")
                else:
                    # Fall back to other selectors
                    for title_selector in ['h2', '.job-title', '[data-cy*="title"]', 'a[href*="/jobs/detail"]']:
                        try:
                            title_elem = current_card.locator(title_selector).first
                            if await title_elem.count() > 0:
                                job_title = await title_elem.text_content()
                                if job_title and len(job_title) > 0:
                                    break
                        except Exception as e:
                            logger.debug(f"Error getting title with selector {title_selector}: {e}")
                
                logger.info(f"Processing job {i+1}: {job_title}")
                
                # Try two approaches:
                # 1. If we have a job ID, try direct navigation
                if job_id:
                    try:
                        job_url = DICE_JOB_URL_PATTERN.format(job_id)
                        logger.info(f"Navigating directly to: {job_url}")
                        new_page = await self.context.new_page()
                        await new_page.goto(job_url, timeout=15000)
                        await new_page.wait_for_load_state("networkidle")
                        
                        # Process the job details page
                        success = await self._process_job_detail_page(new_page, job_title)
                        if success:
                            total_applied += 1
                            logger.info(f"Total jobs applied: {total_applied}/{max_applications}")
                        continue  # Skip the click approach below
                    except Exception as e:
                        logger.error(f"Error navigating directly to job URL: {e}")
                        # Close the page and fall back to clicking
                        try:
                            await new_page.close()
                        except:
                            pass
                
                # 2. Fall back to clicking the card
                logger.info("Falling back to clicking the job card")
                await current_card.click()
                
                # Wait for new tab to open
                try:
                    new_page = await self.context.wait_for_page(timeout=10000)
                    await new_page.wait_for_load_state("networkidle")
                    
                    # Process the job details page
                    success = await self._process_job_detail_page(new_page, job_title)
                    if success:
                        total_applied += 1
                        logger.info(f"Total jobs applied: {total_applied}/{max_applications}")
                except Exception as e:
                    logger.error(f"Error waiting for new tab: {e}")
                    # Try to continue with next job
                
            except Exception as e:
                logger.error(f"Error processing job {i+1}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Close any extra tabs and continue
                try:
                    pages = self.context.pages
                    if len(pages) > 1:
                        for extra_page in pages[1:]:
                            await extra_page.close()
                except:
                    pass
            
            # Wait before processing next job
            await page.wait_for_timeout(1000)
            
        logger.info(f"Job processing complete. Applied to {total_applied} jobs.")
    
    async def _process_job_detail_page(self, page, job_title):
        """Process a job detail page and apply if possible"""
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot of job details
        await page.screenshot(path=f"logs/job_details_{job_title.replace(' ', '_')}.png")
        
        # Extract job details
        job_description = ""
        for desc_selector in ['[data-cy="job-description"]', '.job-description', '#jobDescription']:
            desc_elem = page.locator(desc_selector).first
            if await desc_elem.count() > 0:
                job_description = await desc_elem.text_content()
                logger.info(f"Found job description ({len(job_description)} chars)")
                break
        
        if not job_description:
            logger.warning("Could not find job description")
            job_description = await page.locator('body').text_content()
        
        # Look for Apply Now button
        apply_button = None
        for apply_selector in [
            'button:has-text("Apply now")',
            'button:has-text("Apply Now")', 
            '[data-cy="apply-button"]',
            'a:has-text("Apply")',
            'button:has-text("Apply")',
            'a[href*="apply"]',
            '.apply-button'
        ]:
            button = page.locator(apply_selector).first
            if await button.count() > 0 and await button.is_visible():
                logger.info(f"Found apply button with selector: {apply_selector}")
                apply_button = button
                break
        
        if apply_button:
            # Click Apply button
            await apply_button.click()
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            
            # Take screenshot after clicking apply
            await page.screenshot(path=f"logs/apply_form_{job_title.replace(' ', '_')}.png")
            
            # Handle the application process
            application_result = await self.handle_application(page, job_description, job_title)
            
            # Close the job details tab
            await page.close()
            return application_result
        else:
            logger.warning(f"No Apply button found for job: {job_title} - likely already applied")
            # Log as already applied
            with open("logs/already_applied.log", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Already applied to: {job_title} at {page.url}\n")
            
            await page.close()
            return False

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
            # Check for "Next" button first (multi-step application)
            next_button = None
            for next_selector in ['button:has-text("Next")', '[data-cy="next-button"]']:
                button = page.locator(next_selector).first
                if await button.count() > 0:
                    logger.info(f"Found Next button with selector: {next_selector}")
                    next_button = button
                    break
                    
            if next_button:
                await next_button.click()
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(2000)
                
            # Look for submit button
            submit_button = None
            for submit_selector in [
                'button:has-text("Submit")',
                'button[type="submit"]',
                '[data-cy="submit-application"]',
                '.submit-button'
            ]:
                button = page.locator(submit_selector).first
                if await button.count() > 0:
                    logger.info(f"Found submit button with selector: {submit_selector}")
                    submit_button = button
                    break
                    
            if submit_button:
                # If the button is disabled, we might have missed something required
                if await submit_button.is_disabled():
                    logger.warning("Submit button is disabled. Taking screenshot to troubleshoot.")
                    await page.screenshot(path=f"logs/disabled_submit_{job_title.replace(' ', '_')}.png")
                    # Try to fill required fields
                    await self._fill_required_fields(page)
                
                # Try clicking submit again
                if not await submit_button.is_disabled():
                    await submit_button.click()
                    logger.info(f"Application submitted for: {job_title}")
                    
                    # Log success
                    with open("logs/successful_applications.log", "a") as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Applied to job: {job_title} at {page.url}\n")
                    
                    # Wait for confirmation
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=f"logs/application_result_{job_title.replace(' ', '_')}.png")
                    return True
                else:
                    logger.warning(f"Submit button remained disabled for: {job_title}")
                    return False
            else:
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
    
    async def _fill_required_fields(self, page):
        """Fill any required fields in the application form"""
        logger.info("Checking for required fields to fill")
        
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
            logger.info("No resume upload field found - may not be required at this step")
        
        # Handle radio buttons - select "Yes" options
        radio_groups = await page.locator('input[type="radio"]').all()
        if len(radio_groups) > 0:
            logger.info(f"Found {len(radio_groups)} radio buttons, selecting positive options")
            yes_radios = page.locator('label:has-text("Yes") input[type="radio"], input[type="radio"][value="yes"]')
            for i in range(await yes_radios.count()):
                radio = yes_radios.nth(i)
                if not await radio.is_checked():
                    await radio.check()
                    logger.info(f"Selected 'Yes' radio button {i+1}")

async def main():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    bot = DiceBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main()) 