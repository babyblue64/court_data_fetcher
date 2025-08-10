#! /usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from read_captcha import quick_read_captcha
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Dict, Optional

def run_scraper(case_type: str, case_number: str, case_year: str) -> Dict[str, Optional[str]]:
    """Main function to enter data, bypass captcha, scrape data and download pdf"""
    
    # Set firefox so that pdf is auto-downloadable
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.getcwd())
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", True)

    options.add_argument("--headless") # enable headless mode to prevent firefox window from opening
    
    driver = webdriver.Firefox(options=options)
    
    try:
        # Open website
        driver.get("https://hcmadras.tn.gov.in/case_status_mas.php")
        time.sleep(1)

        # Fill forms
        case_type_field = driver.find_element(By.NAME, "case_type_name")
        case_type_field.clear()
        case_type_field.send_keys(case_type)
        time.sleep(1)
        case_type_field.send_keys(Keys.ENTER)
        time.sleep(1)

        case_number_field = driver.find_element(By.NAME, "RegCase_no")
        case_number_field.send_keys(case_number)

        case_year_field = driver.find_element(By.NAME, "RegCase_year")
        case_year_field.send_keys(case_year)

        # Solving captcha part
        if not solve_captcha_and_submit(driver):
            raise Exception("Failed to solve captcha after multiple attempts")

        # Wait for data to load ( upto 70 seconds )
        WebDriverWait(driver, 70).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#example > tbody"))
        )

        # Scraping part
        result = {
            "petitioner": extract_text(driver, "#example > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(2)"),
            "respondent": extract_text(driver, "#example > tbody:nth-child(1) > tr:nth-child(7) > td:nth-child(2)"),
            "filing_date": extract_text(driver, "#example > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(4)"),
            "next_hearing_date": extract_last_hearing_date(driver),
            "error": None
        }

        # Download PDF
        download_pdf(driver)

        return result

    except Exception as e:
        if "No record found" in str(e):
            return {"error": "No record found for the given case details"}
        raise Exception(f"Scraping failed: {str(e)}")
    finally:
        driver.quit()

def solve_captcha_and_submit(driver, max_attempts: int = 5) -> bool:
    """Handle captcha solving recursively"""
    for attempt in range(1, max_attempts + 1):
        try:
            # take screenshot of captcha
            captcha_img = driver.find_element(By.ID, "contact_captcha_img")
            captcha_img.screenshot("captcha.png")
            time.sleep(1)
            
            # Solve for captcha
            result = quick_read_captcha('captcha.png')
            os.remove('captcha.png')
            
            if not result:
                continue
            
            # fill captcha and submit
            captcha_input = driver.find_element(By.NAME, "caseno_captcha")
            captcha_input.clear()
            captcha_input.send_keys(result)
            driver.find_element(By.ID, "submit").click()
            
            time.sleep(2)
            error_div = driver.find_element(By.ID, "caseno_search_result")
            error_text = error_div.get_attribute('innerHTML')
            
            if "No record found" in error_text:
                raise Exception("No record found for the given case details")
            if "Captcha not matching" not in error_text:
                return True
                
        except Exception as e:
            if "No record found" in str(e):
                raise  # Re-raise the "No record found" exception to be handled upstream
            print(f"Attempt {attempt} failed: {str(e)}")
    
    return False

def extract_text(driver, selector: str) -> Optional[str]:
    """extract helper func"""
    try:
        return driver.find_element(By.CSS_SELECTOR, selector).text
    except:
        return None

def extract_last_hearing_date(driver) -> Optional[str]:
    """extract latest value in hearing date column"""
    try:
        hearing_dates = driver.find_elements(By.XPATH, "//table[@id='example7']//tr/td[5][normalize-space()]")
        return hearing_dates[-1].text if hearing_dates else None
    except:
        return None

def download_pdf(driver):
    """PDF download helper"""
    try:
        pdf_form = WebDriverWait(driver, 70).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form[action='order_view.php']"))
        )
        pdf_button = driver.find_element(By.CSS_SELECTOR, "button.pdf_but")
        pdf_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"PDF download failed : {e}")