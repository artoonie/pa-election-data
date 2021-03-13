from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

import os
import time

class DownloadPennElectionData():
    def __init__(self):
        self.ss_number = 0
        self.driver = self.create_driver()
        self.downloads_dir = './downloads/'
        self.starting_index = 1  # starting index is 1, first index is "Select Election"

        # Continue where we left off - assuming it broke at some point
        # self.starting_index += len(os.listdir(self.downloads_dir))
        self.starting_index += 36

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

    def download_file(self):
        time.sleep(4)
        self.driver.find_element_by_id('ChkAllOfficeChecked').click()
        self.driver.find_element_by_id('ChkAllCandidateChecked').click()
        self.driver.find_element_by_id('ChkAllPartyChecked').click()

        reportTypeSelector = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[3]/div[1]/select')
        reportTypeOptions = Select(reportTypeSelector)
        reportTypeOptions.select_by_visible_text('Statewide')

        exportTypeSelector = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[3]/div[2]/select')
        exportTypeOptions = Select(exportTypeSelector)
        exportTypeOptions.select_by_visible_text('CSV')

        submitButton = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[5]/div[3]/button')
        submitButton.click()
        print("Beginning download")
        time.sleep(1)
        print("Done")

    def download_all_files(self):
        url = 'https://www.electionreturns.pa.gov/ReportCenter/Reports'
        self.driver.get(url)
        time.sleep(1)

        electionSelector = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/div[2]/div/div[1]/div[1]/select')
        electionOptions = Select(electionSelector)
        election_index = self.starting_index
        while True:
            print("Starting on file", election_index)
            try:
                electionOptions.select_by_index(election_index)
            except NoSuchElementException:
                print("Found all of em!")
                break
            election_index += 1

            print("Selected", electionOptions.first_selected_option.text)

            try:
                self.download_file()
            except Exception as e:
                print("There was an error. Screenshot will be saved - can you tell what's wrong?")
                self.debug_screenshot()
                raise e

d = DownloadPennElectionData()
d.download_all_files()