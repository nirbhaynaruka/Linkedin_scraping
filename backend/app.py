from flask import Flask, request, jsonify
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import chromedriver_autoinstaller
from flask_cors import CORS
from flask import send_from_directory
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
CSV_FOLDER = os.path.join(os.getcwd(), 'csv_files')


if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)
def get_driver():
    # Ensure ChromeDriver is installed or updated automatically
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)

def get_text_safe(element, index=None):
    if isinstance(element, list):
        if index is not None and len(element) > index:
            return element[index].text.strip()
        else:
            return "NA"
    return element.text.strip() if element else "NA"

def scrape_jobs(job_name, country_name, time_range):
    driver = get_driver()
    print("Chrome version:", driver.capabilities['browserVersion'])
    print("ChromeDriver version:", driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])

    wait = WebDriverWait(driver, 15)

    final_url = f"https://www.linkedin.com/jobs/search/?keywords={job_name.replace(' ', '%20')}&location={country_name.replace(' ', '%20')}"
    driver.get(final_url)

    for _ in range(4):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(3)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    time.sleep(2)
    job_listing_divs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'job-search-card')]")))
    job_ids = [div.get_attribute('data-entity-urn').split(':')[-1] for div in job_listing_divs if div.get_attribute('data-entity-urn')]

    jobs_df = pd.DataFrame(columns=["Date Scraped","Job Title", "Company Name", "Location", "Salary Range", "Date Posted", "Applicants", "Job Level", "Industry", "Description", "Recruiter Name", "Recruiter Position", "Job Link"])
    # job_ids = [  '3852161408', '3875625943']
    for job_id in job_ids:
        job_url= f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        job_urll = f"https://www.linkedin.com/jobs/search/?currentJobId={job_id}&keywords={job_name.replace(' ', '%20')}&location={country_name.replace(' ', '%20')}"
        driver.get(job_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(2)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        job_details = {
            "Date Scraped" : datetime.now().strftime('%Y-%m-%d'),
            "Job Title": get_text_safe(soup.find('h2', class_="top-card-layout__title")),
            "Company Name": get_text_safe(soup.find('a', class_="topcard__org-name-link topcard__flavor--black-link")),
            "Location": get_text_safe(soup.find('span', class_="topcard__flavor topcard__flavor--bullet")),
            "Salary Range": get_text_safe(soup.find('div',class_="salary compensation__salary")),
            "Date Posted": get_text_safe(soup.find('span', class_="posted-time-ago__text")),
            "Applicants": get_text_safe(soup.select_one('span.num-applicants__caption, figcaption.num-applicants__caption')),
            "Job Level": get_text_safe(soup.find('span', class_="description__job-criteria-text description__job-criteria-text--criteria")),
            "Industry": get_text_safe(soup.find_all(class_="description__job-criteria-text description__job-criteria-text--criteria"), 3),
            "Description": get_text_safe(soup.find('div', class_="show-more-less-html__markup")),
            "Recruiter Name": get_text_safe(soup.find('h3', class_="base-main-card__title")),
            "Recruiter Position": get_text_safe(soup.find('h4', class_="base-main-card__subtitle")),
            "Job Link": job_urll
        }
        jobs_df = pd.concat([jobs_df, pd.DataFrame([job_details])], ignore_index=True)

    driver.quit()
    csv_filename = f"{job_name.replace(' ', '_')}_{country_name.replace(' ', '_')}.csv"
    file_exists, new_rows_added = merge_and_save_data(jobs_df, csv_filename)
    return file_exists, new_rows_added, csv_filename


@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    job_name = data.get('job_name', '').strip()
    country_name = data.get('country_name', '').strip()
    time_range = data.get('time_range','').strip()

    file_exists, new_rows_added, csv_filename = scrape_jobs(job_name, country_name,time_range)
    message = f"{'Updated' if file_exists else 'Created'} {csv_filename} with {new_rows_added} new rows."
    
    return jsonify({"message": message, "filename": csv_filename}), 200

def merge_and_save_data(new_data, filename):
    csv_path = os.path.join('csv_files', filename)

    if os.path.exists(csv_path):
        existing_data = pd.read_csv(csv_path)
    else:
        existing_data = pd.DataFrame()

    combined_data = pd.concat([new_data,existing_data], ignore_index=True)
    final_data = combined_data.drop_duplicates(subset=['Job Link'], keep='first')
    final_data.to_csv(csv_path, index=False)
    return os.path.exists(csv_path), len(final_data) - len(existing_data)


@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(CSV_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
