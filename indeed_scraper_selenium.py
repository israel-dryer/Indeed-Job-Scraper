import csv
from datetime import datetime
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


def get_url(position, location):
    """Generate url from position and location"""
    template = 'https://www.indeed.com/jobs?q={}&l={}'
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    url = template.format(position, location)
    return url


def get_record(card):
    """Extract job data from single card"""
    job_title = card.find_element_by_class_name('jobtitle').text
    company = card.find_element_by_class_name('company').text
    location = card.find_element_by_class_name('location').text
    post_date = card.find_element_by_class_name('date').text
    extract_date = datetime.today().strftime('%Y-%m-%d')
    summary = card.find_element_by_class_name('summary').text
    job_url = card.find_element_by_class_name('jobtitle').get_attribute('href')
    return job_title, company, location, post_date, extract_date, summary, job_url


def get_page_records(cards, job_list, url_set):
    """Extract all cards from the page"""
    for card in cards:
        record = get_record(card)
        # add if job title exists and not duplicate
        if record[0] and record[-1] not in url_set:
            job_list.append(record)
            url_set.add(record[-1])


def save_data_to_file(records):
    """Save data to csv file"""
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'JobUrl'])
        writer.writerows(records)


def main(position, location):
    """Run the main program routine"""
    scraped_jobs = []
    scraped_urls = set()
    
    url = get_url(position, location)
    
    # setup web driver
    options = EdgeOptions()
    options.use_chromium = True
    driver = Edge(options=options)
    driver.implicitly_wait(5)
    driver.get(url)        
    
    # extract the job data
    while True:
        cards = driver.find_elements_by_class_name('jobsearch-SerpJobCard')
        get_page_records(cards, scraped_jobs, scraped_urls)
        try:
            driver.find_element_by_xpath('//a[@aria-label="Next"]').click()
        except NoSuchElementException:
            break
        except ElementNotInteractableException:
            driver.find_element_by_id('popover-x').click()  # to handle job notification popup
            get_page_records(cards, scraped_jobs, scraped_urls)
            continue

    # shutdown driver and save file
    driver.quit()
    save_data_to_file(scraped_jobs)


if __name__ == '__main__':
    main('python developer', 'charlotte nc')
