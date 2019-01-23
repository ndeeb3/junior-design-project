
# coding: utf-8

# In[89]:


import re
import csv
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# In[90]:


url = "http://apps.webofknowledge.com.prx.library.gatech.edu/UA_GeneralSearch_input.do?product=UA&SID=5Bmu1zxN36Unjxtugwz&search_mode=GeneralSearch"
#Enter your gatech credentials here.
#I've got it so that it actually opens up a browser and shows you what it's doing
#Also bc I can't get 2FA to work yet automatically
username = "USERNAME_HERE"
password = "PASSWORD_HERE"


# In[91]:


def scraperMain(browser):

    username_field = browser.find_element_by_id("username")
    password_field = browser.find_element_by_id("password")
    submit_button = browser.find_element_by_name("submit")

    username_field.send_keys(username)
    password_field.send_keys(password)
    submit_button.click()
    
    #TODO: Automate 2FA
    #browser.switch_to.default_content()
    #iframe = browser.find_element_by_id("duo_iframe")
    #browser.switch_to.frame(iframe)
    #print("Swapped to frame.")
    #tfa_button = browser.find_element_by_class_name("row-label")
    #tfa_button.click()

    print("Manually do 2FA.")
    wait = WebDriverWait(browser, 42)
    temp = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"value(input1)\"]")))
    print("WOS loaded.")
    
    words_dict = open_csv("braveNewWords.csv")
    
    try:
        #Words_correlated is a list filled with 5-tuples
        #The 5-tuple has the structure:
        #(Word, year it entered lexicon, total # of hits in WOS,
        #dict for publishing year distribution,
        #dict for domain distribution)
        words_correlated = []
        for word, year in words_dict.items():
            hits, year_dict, domain_dict = searchTerm(browser, word)
            f_tuple = (word, year, hits, year_dict, domain_dict)
            words_correlated.append(f_tuple)
            if hits:
                print(f_tuple)
            
            #return to main search screen
            browser.get(url)
            wait = WebDriverWait(browser, 42)
            temp = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"value(input1)\"]")))
            
        browser.quit()
        
        #print(words_correlated)
    except Exception as e:
        print(e)
        browser.quit()


# In[92]:


def searchTerm(driver, string):
    #Returns (total # of hits, dict of {year, # in that year}, dict of {domain, # in that domain})
    #For a given word
    
    search_bar = driver.find_element_by_xpath("//*[@id=\"value(input1)\"]")
    search_bar.click()
    
    #clearing bar
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    search_bar.send_keys(Keys.DELETE)
    
    search_bar.send_keys(string)
    search_bar.send_keys(Keys.ENTER)
    time.sleep(4)
    
    try:    
        raw_hit_count_element = browser.find_element_by_id("hitCount.top")
        raw_hit_count = raw_hit_count_element.text
        
        year_stats_link = driver.find_element_by_class_name("link-style1")
        year_stats_link.click()
        time.sleep(2)
        
        year_stats_dict, domains_stats_dict = detailsHarvest(browser)
        #print(year_stats_dict)
        return raw_hit_count, year_stats_dict, domains_stats_dict
        
    except:
        #TODO: Handle this case
        print("No/minimal stats on publication years for word " + string)
        return None, None, None


# In[93]:


def yearRegex(string):
    yearPattern = re.compile("[1,2][0-9][0-9][0-9]\ \(.*")
    year = yearPattern.search(string)
    if year:
        return year.group()
    return None

def yearSplitter(string):
    yearPattern = re.compile("[1,2][0-9][0-9][0-9]")
    yearMatch = yearPattern.search(string)
    year = str(yearMatch.group())
    
    #this regex is adorable ---v
    numPattern = re.compile("\(.*\)")
    numMatch = numPattern.search(string)
    number = str(numMatch.group())
    number = re.sub("(\(|\)|,)", "", number)
    return year, number

def domainsRegex(string):
    return None
    #TODO
    
def domainsSplitter(string):
    return None
    #TODO


# In[94]:


def detailsHarvest(driver):
    year_stats_elements = driver.find_elements_by_tag_name("label")
    year_stats_dict = {}
    domains_stats_dict = {}
    for e in year_stats_elements:
        element_text = e.text
        if yearRegex(element_text):
            e1, e2 = yearSplitter(element_text)
            year_stats_dict[e1] = e2
        #TODO domains parsing
    return year_stats_dict, domains_stats_dict


# In[95]:


def open_csv(file):
    words_dict = {}
    with open(file, "r", encoding = "utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row):
                words_dict[row[0]] = row[1]
    return words_dict


# In[96]:


browser = webdriver.Chrome()
browser.get(url)

scraperMain(browser)


# In[97]:


browser.quit()
