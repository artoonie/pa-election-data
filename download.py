from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

import glob
import os
import time

class DownloadPennElectionData():
    def __init__(self):
        self.ss_number = 0
        self.driver = self.create_driver()
        self.downloads_dir = './downloads/'
        self.starting_index = 1  # starting index is 1, first index is "Select Election"

        # Continue where we left off - assuming it broke at some point
        self.starting_index += len(os.listdir(self.downloads_dir))

        if self.starting_index > 47:
            # Add 1 to make up for this non-downloaded file in the list.
            # Otherwise we'll re-download one file, which will trigger the don't-override logic
            print("You have already passed the 2015 special election, which we skipped.")
            self.starting_index += 1

    def debug_screenshot(self):
        filename = f'screenshot_{self.ss_number}.png'
        print("Saving screenhot to", filename)
        self.driver.save_screenshot(filename)
        self.ss_number += 1

    def create_driver(self):
        chromeOptions = webdriver.chrome.options.Options()
        chromeOptions.add_argument('--headless')
        chromeOptions.add_experimental_option('prefs', 
                {'download': 
                    {'default_directory': './downloads/',
                     'directory_upgrade': True,
                     'extensions_to_open': ''}
                })

        driver = webdriver.Chrome(options=chromeOptions)

        driver.implicitly_wait(10)
        return driver

    def num_downloaded_files(self):
        return len(os.listdir(self.downloads_dir))

    def get_latest_download(self):
        list_of_files = glob.glob(os.path.join(self.downloads_dir, '*.CSV'))
        return max(list_of_files, key=os.path.getctime)

    def make_filename_safe(self, string):
        chars = "".join([c for c in string if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        chars = chars.replace(' ', '_')
        return chars

    def rename_latest_file_using_title(self, election_name):
        from_file = self.get_latest_download()
        to_file = os.path.join(self.downloads_dir, self.make_filename_safe(election_name)) + ".CSV"
        os.rename(from_file, to_file)

    def download_file(self, election_name):
        time.sleep(4)  # Give breathing room for everything dynamic to settle
        self.driver.find_element_by_id('ChkAllOfficeChecked').click()
        self.driver.find_element_by_id('ChkAllCandidateChecked').click()
        self.driver.find_element_by_id('ChkAllPartyChecked').click()

        report_type_selector = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[3]/div[1]/select')
        report_type_options = Select(report_type_selector)
        report_type_options.select_by_visible_text('Statewide')

        export_type_selector = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[3]/div[2]/select')
        export_type_options = Select(export_type_selector)
        export_type_options.select_by_visible_text('CSV')

        orig_num_files = self.num_downloaded_files()
        submit_button = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[5]/div[3]/button')
        submit_button.click()

        print("Beginning download")
        count = 0
        while self.num_downloaded_files() == orig_num_files:
            count += 1
            print(".")
            if count > 20:
                raise RuntimeError("Failed to download after 20 seconds")
            time.sleep(1)
        self.rename_latest_file_using_title(election_name)
        print("Download complete")

    def download_all_files(self):
        url = 'https://www.electionreturns.pa.gov/ReportCenter/Reports'
        self.driver.get(url)
        time.sleep(1)

        election_selector = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[1]/div[1]/select')
        election_options = Select(election_selector)
        election_index = self.starting_index
        errorCount = 0
        while True:
            print("Starting on file", election_index)
            try:
                election_options.select_by_index(election_index)
            except NoSuchElementException:
                print("Found all of em!")
                break

            election_name = election_options.first_selected_option.text
            print("Selected", election_name)
            if election_name == "2015 Special Election 5th Senatorial District":
                print("Skipping - we know this one has no data and causes a failure")
                election_index += 1
                continue

            try:
                self.download_file(election_name)
            except Exception as e:
                errorCount += 1
                print("There was an error. Screenshot will be saved - can you tell what's wrong?")
                self.debug_screenshot()
                if errorCount > 10:
                    raise e
                else:
                    print(e)

                # cool off period, then skip the increment
                time.sleep(10*errorCount)
                continue

            election_index += 1

d = DownloadPennElectionData()
d.download_all_files()
