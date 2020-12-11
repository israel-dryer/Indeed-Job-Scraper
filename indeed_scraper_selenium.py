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


def save_data_to_file(records):
    """Save data to csv file"""
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'JobUrl'])
        writer.writerows(records)


def main(position, location):
    """Run the main program routine"""
    records = []
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
        for card in cards:
            record = get_record(card)
            records.append(record)
        try:
            driver.find_element_by_xpath('//a[@aria-label="Next"]').click()
        except NoSuchElementException:
            break
        except ElementNotInteractableException:
            driver.find_element_by_id('popover-x').click()  # to handle job notification popup
            continue

    # shutdown driver and save file
    driver.quit()
    save_data_to_file(records)


if __name__ == '__main__':
    main('senior accountant', 'charlotte nc')
