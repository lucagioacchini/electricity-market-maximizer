from datetime import datetime
import time
from pathlib import Path
import os
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from src.common.config import *

import logging
import logging.config

# logging.config.fileConfig('src/logging.conf')
# logger = logging.getLogger(__name__)
#path=(Path.cwd())
#path = str(path.parents[1] / 'downloads')

class TernaSpider():
    def __init__(self):
        profile = webdriver.FirefoxProfile()  # path -- gekodriver
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference(
            "browser.download.manager.showWhenStarting",
            False
        )
        profile.set_preference("browser.download.dir", DOWNLOAD)
        profile.set_preference("browser.download.downloadDir", DOWNLOAD)
        profile.set_preference("browser.download.defaultFolder", DOWNLOAD)
        profile.set_preference(
        	"browser.helperApps.neverAsk.saveToDisk", 
            "application/vnd.openxmlformats-officedocument.spreadsheetml."\
            "sheet, application/-csv"
    	)

        self.driver = webdriver.Firefox(
            profile, 
            log_path='logs/geckodrivers.log'
        )
        self.driver.set_page_load_timeout(20)
        self.action = ActionChains(self.driver)


    def getData(self, url, start, end):
        self.driver.get(url)
        self.driver.switch_to.frame(
            self.driver.find_element_by_id("iframeEnergyBal")
        )

        while True:
            try:
                wait(self.driver, 1).until(
                    ec.frame_to_be_available_and_switch_to_it((
                        By.XPATH, 
                        '/html/body/div/iframe'
                    ))
                )
                break
            except TimeoutException:
                time.sleep(1)
            
        while True:
            try: 
                parent = self.driver.find_element_by_class_name("canvasFlexBox")   
                # Div
                btn = parent.find_element_by_css_selector(
                    "visual-container-modern.visual-container-component:nth"\
                    "-child(34) > transform:nth-child(1) > div:nth-child(1) "\
                    "> div:nth-child(3) > visual-modern:nth-child(1) "\
                    "> div:nth-child(1)"
                )
                self.driver.execute_script('arguments[0].click();', btn)
                
                while True:
                    try:
                        wait(parent, 1).until(
                            ec.visibility_of_element_located((
                                By.TAG_NAME, 
                                'input'
                            ))
                        )
                        break
                    except TimeoutException:
                        time.sleep(1)
                
                #Inputs
                form = parent.find_elements_by_tag_name("input")
                self.driver.execute_script('arguments[0].click();', form[0])
                time.sleep(1)
                form[0].send_keys(start)
                self.driver.execute_script('arguments[0].click();', form[1])
                time.sleep(1)
                form[1].send_keys(end)
                
                # Graph
                graph = self.driver.find_element_by_css_selector(
                    "#pvExplorationHost > div > div > exploration > div "\
                    "> explore-canvas-modern > div > div.canvasFlexBox > div "\
                    "> div.displayArea.disableAnimations.fitToPage "\
                    "> div.visualContainerHost > visual-container-repeat "\
                    "> visual-container-modern:nth-child(23) > transform"
                )
                self.driver.execute_script('arguments[0].click();', graph)
                self.action.move_to_element(graph).perform()
                
                # Options
                btn = parent.find_element_by_class_name('vcMenuBtn')
                self.driver.execute_script('arguments[0].click();', btn)
                self.action.move_to_element(btn).perform()
                
                # Export Data
                btn = parent.find_element_by_xpath(
                    "/html/body/div[9]/drop-down-list/ng-transclude/"\
                    "ng-repeat[1]/drop-down-list-item/ng-transclude/ng-switch/"\
                    "div"
                )
                self.action.move_to_element(btn).perform()
                self.driver.execute_script('arguments[0].click();', btn)
                break

            except NoSuchElementException:
                time.sleep(1)

        while True:
            try:
                # Download button
                btn = self.driver.find_element_by_class_name("primary") 
                self.driver.execute_script('arguments[0].click();', btn)
                break       
            except NoSuchElementException:
                time.sleep(1)
            
        self.setFname(start)

    def setFname(self, date):
        date = date.replace('/','')
        while True:
            for files in Path(DOWNLOAD).iterdir():
                if 'data.xlsx' in str(files):
                    target = Path(f"{DOWNLOAD}/{TERNA['name']}{date}.xlsx")
                    time.sleep(2)
                    files.replace(target)
                    
                    QUEUE.put(f"{TERNA['name']}{date}.xlsx")
                    return None
        time.sleep(1)