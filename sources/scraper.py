from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException
import pdfkit
import os
from sources.captcha_module import CaptchaSolver
# from captcha_module import CaptchaSolver
import os
import time
import zipfile
import uuid
from datetime import datetime
from weasyprint import HTML
import os
import shutil

def zip_directory(folder_path, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Arcname ensures correct folder structure inside zip
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)

# Example usage
# zip_directory('my_folder', 'my_folder.zip')

class WebScraper:
    def __init__(self, data):
        self.driver = None
        self.data = data
        self.state_code = data.get('state_code')
        self.dist_code = data.get('dist_code')
        self.complex_code_raw = data.get('court_complex')
        self.court_name = data.get('court_name')
        self.date = data.get('date')
        unique_id = str(uuid.uuid4())
        now = datetime.now()
        self.date_str = now.strftime("%Y%m%d%H%M%S")

        self.base_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        self.dir = os.path.join(self.base_dir, self.date_str)
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        self.criminal_files = os.path.join(self.dir, "criminal")
        self.civil_files = os.path.join(self.dir, "civil")

        

        if not os.path.exists(self.civil_files):
            os.makedirs(self.civil_files)

        if not os.path.exists(self.criminal_files):
            os.makedirs(self.criminal_files)

    # Create a zip file from multiple directories
    def create_zip_from_dirs(self, zip_filename, dirs):
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for dir_path in dirs:
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Store files with relative paths
                        arcname = os.path.rzip_filenameelpath(file_path, start=os.path.commonpath(dirs))
                        zipf.write(file_path, arcname)
        print(f"Created zip file: {zip_filename}")


    # Function to create a zip file
    def create_zip(self, zip_filename, files_to_zip):
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in files_to_zip:
                zipf.write(file, os.path.basename(file))

    # Function to delete the zip file after 5 minutes
    def delete_after_timeout(self, zip_filename, timeout=300):
        time.sleep(timeout)  # Wait for 5 minutes (300 seconds)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            print(f"{zip_filename} has been deleted after {timeout // 60} minutes.")
        else:
            print(f"{zip_filename} does not exist anymore.")

    def start_scraping(self):
        try:
            print("=============scraping-started============")
            options = Options()
            options.add_argument("--headless")  # Headless mode
            options.add_argument("--disable-gpu")  # Good practice
            options.add_argument("--no-sandbox")  # Required for some Linux distros
            options.add_argument("--window-size=1920,1080")  # Ensure full content renders


            service = Service("/usr/bin/chromedriver")  # Point to the correct chromedriver
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list")

            time.sleep(3)  # Wait for page to load

            state_list = driver.find_elements(By.XPATH, '//*[@id="sess_state_code"]/option')
            states = [{"state": state.text, "value": state.get_attribute("value")} for state in state_list]
            # print(states)
            # Select a state

            print("================states found================")
            state_select = Select(driver.find_element(By.ID, "sess_state_code"))
        
            state_select.select_by_value(self.state_code)  # Select valid state by mock value
            print(f"=============Selected state: {self.state_code}==============")

            time.sleep(2)  # Wait for JS to populate next dropdown
            # Select a district

            dist_list = driver.find_elements(By.XPATH, '//*[@id="sess_dist_code"]/option')
            districts = [{"district": dist.text, "value": dist.get_attribute("value")} for dist in dist_list]

            # print(districts)

            print("================districts found================")
            district_select = Select(driver.find_element(By.ID, "sess_dist_code"))
            district_select.select_by_value(self.dist_code )  # Use actual district value
            print(f"=============Selected district: {self.dist_code}==============")

                
            time.sleep(2)  # Wait for JS to populate next dropdown

            complex_list = driver.find_elements(By.XPATH, '//*[@id="court_complex_code"]/option')
            complexes = [{"complex": comp.text, "value": comp.get_attribute("value")} for comp in complex_list]

            # print(complexes)
            # Select a court complex

            print("================complexes found================")
            complex_select = Select(driver.find_element(By.ID, "court_complex_code"))
            complex_select.select_by_value(self.complex_code_raw)  # Use actual complex value
            print(f"=============Selected complex: {self.complex_code_raw}==============")

            time.sleep(2)  # Wait for JS to populate next dropdown

            # court_est_code

            try:    
            
                try:
                    alert = driver.switch_to.alert
                    print("Alert found:", alert.text)
                    # To accept the alert (click OK):
                    alert.accept()
                    # Or to dismiss (click Cancel):
                    # alert.dismiss()
                except NoAlertPresentException:
                    print("No alert is present")
                time.sleep(2)

                # est_list = driver.find_elements(By.XPATH, '//*[@id="court_est_code"]/option')
                # establishment_list = [{"est": est.text, "value": est.get_attribute("value")} for est in est_list]

                # # print(complexes)
                # # Select a court complex

                # print("================establishment_list found================", establishment_list)
                # establishment_select = Select(driver.find_element(By.ID, "court_est_code"))
                # establishment_select.select_by_value(establishment_list[i]["value"])  # Use actual complex value
                # print(f"=============Selected establishment: {establishment_list[i]['est']}==============")    
    
                time.sleep(2)  # Wait for JS to populate next dropdown
            except Exception as e:
                print("==========errror============", e)

            court_list = driver.find_elements(By.XPATH, '//*[@id="CL_court_no"]/option')
            courts = [{"court": court.text, "value": court.get_attribute("value")} for court in court_list]

            # print(courts)
            # Select a court complex
     
            print("================courts found================")
            court_select = Select(driver.find_element(By.ID, "CL_court_no"))

            court_select.select_by_value(self.court_name)  # Use actual court value
            print(f"=============Selected court: {self.court_name}==============")


            time.sleep(2)  # Wait for JS to populate next dropdown

            print("================date found================")
            date = driver.find_element(By.ID, "causelist_date")
            date.clear()
            # convert yyyy-mm-dd to dd-mm-yyyy
            date_now = '-'.join(self.date.split('-')[::-1])
            date.send_keys(date_now)  # Use actual date value
            print(f"=============Selected date: {date_now}==============")
            print(f"=============Selected court: {date_now}==============")


            time.sleep(2)  # Wait for JS to populate next dropdown

            for i in range(2):  # Retry mechanism
                j=0
                while True:
                    flag = 0
                    # if i == 0 or j != 0:
                    #     try:
                    #         driver.find_element(By.CSS_SELECTOR, '#validateError .btn-close').click()
                    #     except:
                    #         driver.execute_script("document.getElementById('validateError').remove();")

                    time.sleep(1)
                    captcha_img = driver.find_element(By.ID, "captcha_image")
                    captcha_img.screenshot('captcha.png')

                    try:
                        # captcha_url = driver.find_element(By.ID, "captcha_image").get_attribute("src")
                        solver = CaptchaSolver(image_path='captcha.png')
                        captcha_text = solver.solve_captcha()
                        print(f"=========== Captcha Captured: {captcha_text} =============")

                        captcha_input = driver.find_element(By.ID, "cause_list_captcha_code")
                        captcha_input.send_keys(captcha_text)

                        time.sleep(2)
                        
                        # Submit the form
                        if i == 0:
                            driver.execute_script("submit_causelist('civ');") 
                        else:
                            driver.execute_script("submit_causelist('cri');")
                        # submit_button = driver.find_element(By.XPATH, f'//*[@id="frm_causelist"]/div[3]/div[2]/button[{i+1}]')
                        # submit_button.click()
                        time.sleep(2)  # Wait for response
                        modal = driver.find_element(By.ID, "validateError")
                        if modal.is_displayed():
                            driver.execute_script("closeModel({modal_id:'validateError'});")
                            print("Captcha was incorrect, retrying...")
                            flag = 1
                            continue
                    except Exception as e:
                        flag = 1
                        print(f"Captcha handling failed: {e}")

                    if flag == 0 :
                        print("=========== Captcha Solved Successfully ===========")
                        break
                    j+=1

                # driver.save_screenshot('final_page2.png')  # For debugging
                time.sleep(5)  # Wait for page to load
                # Get the HTML of the table
                # file_link = driver.find_element(By.XPATH, '//*[@id="dispTable"]/tbody/tr[4]/td[2]/a')

                # file_links = driver.find_elements(By.CLASS_NAME, 'someclass')
                file_links_element = driver.find_element(By.XPATH, '//*[@id="dispTable"]/tbody')
                file_links = file_links_element.find_elements(By.TAG_NAME, 'a')
                print(f"================file_links found================")
                print(file_links)
                page_no = 1
                print(f"Total files found: {len(file_links)}")
                for link in file_links:
                    driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    time.sleep(1)  # give time to scroll    
                    link.click()
                    time.sleep(2)  # Wait for download to start

                    html_data = driver.find_element(By.ID, "CauseList").get_attribute("outerHTML")

                    # Wrap in basic HTML with styling
                    full_html = f"""
                    <!doctype html>
                    <html lang="en">
                      <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <title>Bootstrap demo</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
                      </head>
                      <body>
                        {html_data}
                        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
                      </body>
                    </html>
                    """

                    html_file_path = os.path.join(os.getcwd(), "sources/cause_list.html")
                    if i == 0:
                        pdf_file_path = os.path.join(self.civil_files, f"{page_no}.pdf")
                    else:
                        pdf_file_path = os.path.join(self.criminal_files, f"{page_no}.pdf")

                    # pdf_file_path = os.path.join(self.civil_files, f"{page_no}.pdf")
                    with open(html_file_path, "w", encoding="utf-8") as f:
                        f.write(full_html)
                    # driver.save_screenshot('final_page.png')  # For debugging

                    HTML(html_file_path).write_pdf(pdf_file_path)
                    # -----------------

                    # Convert to PDF (without header repeating)
                    # pdfkit.from_file(
                    #     html_file_path,
                    #     pdf_file_path,
                    #     options={
                    #         'disable-smart-shrinking': '',
                    #         'margin-top': '10mm',
                    #         'margin-bottom': '10mm',
                    #     }
                    # )

                    print(f"✅ PDF created: {pdf_file_path}")
                    page_no += 1
                    time.sleep(2)

                    # driver.find_element(By.ID, "main_back_CauseList").click()
                    driver.execute_script("main_back('CauseList');")
                    time.sleep(2)

            zip_directory(self.dir, f"{self.dir}.zip")
            time.sleep(2)
            # self.delete_after_timeout(f"{self.dir}.zip")
            time.sleep(1)
            
            if os.path.exists(self.dir):
                try:
                    shutil.rmtree(self.dir)
                    print("Directory removed successfully.")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Directory does not exist.")

        except Exception as e:
            print(f"❌ PDF creation failed: {e}")
            # Clean up
        driver.quit()
        
        print("=============scraping-ended============")
        return f"{self.date_str}.zip"
    
# data = {'state_code': '8', 'dist_code': '24', 'court_complex': '1080060@1,2,3,4@Y', 'court_name': '1^3', 'date': '2025-10-17'}

# scraper = WebScraper(data)
# scraper.start_scraping()

# zip_directory("/home/shubh/Documents/internshala_assignment/output/20251017140448", "/home/shubh/Documents/internshala_assignment/output/20251017140448.zip")