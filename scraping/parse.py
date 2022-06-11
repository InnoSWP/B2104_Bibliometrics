from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Scraper:
    def __init__(self, driver_folder, headless=False):
        self.authors = dict()  # (author id) -> (full data on author)
        self.author_to_paper = dict()  # (person id) -> [(paper id)]
        self.papers = dict()  # (paper id) -> (full data on paper)

        self.authors_num = 0
        self.papers_num = 0
        self.subjects = dict()  # (Area of research) -> (Number of articles)

        path = driver_folder + "chromedriver.exe"
        options = Options()
        options.headless = headless
        self.driver = webdriver.Chrome(path, options=options)
        self.driver.implicitly_wait(5)
        print("Scraper " + str(id(self)) + " created")
        with open('scraping/data.html'):
            pass

    def parse(self):
        self._get_general_university_stats()
        self._get_authors_list()

    # Returns a list of scopus ids
    def _get_authors_list(self):
        print("Scraper " + str(id(self)) + " parses university workers")
        url = "https://www.scopus.com/results/authorNamesList.uri?affiliationId=60105869&" \
              "s=AF--ID%2860105869%29&resultsPerPage=500"
        self.driver.get(url)
        text = self.driver.page_source
        self.driver.quit()
        with open('scraping/data.html', 'w', encoding='utf-8') as file:
            file.write(text)

    def _get_author_data(self, author_id):
        print("Scraper " + str(id(self)) + " parses author " + str(author_id))
        self.driver.get("https://www.scopus.com/authid/detail.uri?authorId=" + str(author_id))
        data = self.driver.page_source
        self.driver.refresh()
        time.sleep(2)
        nums = driver.find_elements(by=By.XPATH, value="//els-typography[@variant='tertiary-header']")
        rects = driver.find_element(by=By.CLASS_NAME,
                        value="highcharts-series.highcharts-series-0.highcharts-column-series.highcharts-tracker").find_elements(
            by=By.CSS_SELECTOR, value="rect")
        pathes=driver.find_element(by=By.CLASS_NAME, value="highcharts-markers.highcharts-series-1.highcharts-line-series"
                                   ".highcharts-tracker").find_elements(by=By.CSS_SELECTOR, value="path")
        print(driver.find_element(by=By.CLASS_NAME, value="AuthorHeader-module__syvlN.margin-size-4-t").text, author_id)
        
        print(f"Documents by author: {nums[0].text}, Citations: {nums[1].text}, H-index: {nums[2].text}")
        
        print("Number of citations by year:")
        for i in rects:
            i1=i.accessible_name.split()
            print(i1[1][0:4]+": "+i1[2][:len(i1[2])-1])
        
        print("Number of papers by year:")
        for i in pathes:
            i1 = i.accessible_name.split()
            print(i1[1][0:4] + ": " + i1[2][:len(i1[2]) - 1])
        self.driver.quit()
        with open('scraping/data.html', 'w', encoding='utf-8') as file:
            file.write(data)

    def _get_general_university_stats(self):
        print("Scraper " + str(id(self)) + " parses university general statistics")

        url = "https://www.scopus.com/affil/profile.uri?afid=60105869"
        self.driver.get(url)

        subject_distribution = self.driver.find_element(By.ID, "subjectList").text.split('\n')
        affiliation_general = self.driver.find_element(By.ID, "affilAddlSec").text.split('\n')

        self.papers_num = int(''.join(affiliation_general[1].split(' ')))  # The line is stored like '1 225', not '1225'
        self.authors_num = int(affiliation_general[3])

        for ind in range(0, len(subject_distribution), 2):
            self.subjects[subject_distribution[ind]] = int(subject_distribution[ind + 1])

        self.driver.quit()

    def _get_papers(self, author_id):
        url = "https://www.scopus.com/results/results.uri?sort=plf-f&src=s&sid=c1140baa70c949831487b6121ec26b3d&sot=aff&sdt=a&sl=15&s=AF-ID%2860105869%29&origin=AffiliationProfile&editSaveSearch=&txGid=2b6475e16d6694003cc51e4df73b6ae1"
        citation_dynamics_url = "https://www.scopus.com/record/pubmetrics.uri?eid=2-s2.0-85054938535&origin=recordpage"
