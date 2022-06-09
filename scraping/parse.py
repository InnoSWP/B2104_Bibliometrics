from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from calendar import month_name


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
        self._get_papers_authors()

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
        self.driver.quit()
        with open('scraping/data.html', 'w', encoding='utf-8') as file:
            file.write(data)

    '''Number of workers, works and distribution of the latter among topics'''

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

    # Parses general information on a selected work: name, list of authors, citations, etc
    def _get_paper_data(self, paper_id):
        print("Scraper " + str(id(self)) + " parses article " + str(paper_id))
        url = "https://www.scopus.com/record/display.uri?eid=2-s2.0-" + \
              str(paper_id) + "&origin=resultslist&featureToggles=FEATURE_NEW_DOC_DETAILS_EXPORT:1"

        self.driver.get(url)
        paper_name = self.driver.find_element(By.CLASS_NAME, 'Highlight-module__1p2SO').text
        authors = self._get_papers_authors()
        overall_citations = 0
        work_percentile = 100
        fwci = 0
        # An article may not yet have any citations
        try:
            citations_info = self.driver.find_element(By.XPATH, '//els-info-field[@href="#metrics"]')
            overall_citations = int(citations_info.get_attribute("value"))
            work_percentile = citations_info.get_attribute("metavalue")
            fwci = self.driver.find_elements(By.CLASS_NAME, 'vertical-highlight.sc-els-info-field')[1]. \
                find_element(By.CLASS_NAME, 'sc-els-info-field.hydrated').text
        except:
            pass

        source_info = self.driver.find_element(By.CLASS_NAME,
                                               'PublicationInformationBar-module__2SO0m.padding-size-8-t'). \
            find_elements(By.CLASS_NAME, 'hydrated')
        source_name = source_info[0].text  # name of a journal/conference/publisher

        months = {m.lower() for m in month_name[1:]}
        # Date of publishing does not have a static place
        publishing_date = None
        for info in source_info:
            if any([month in info.text.lower() for month in months]):
                publishing_date = info.text
                break

        keywords = self.driver.find_elements(By.CLASS_NAME, 'margin-size-4-t')[-1].text.split('; ')

        publishing_data = self.driver.find_elements(By.CLASS_NAME,
                                                    'stack.stack--xxs.stack--mode-container.stack--vertical.'
                                                    'stack--start.margin-size-0')[:4]
        document_type = publishing_data[0].text.split('\n')[1]  # Is a work article or book
        if '•' in document_type:
            document_type = document_type.split('•')[0]
        source_type = publishing_data[1].text.split('\n')[1]  # where the work was presented
        issn_isbn = publishing_data[2].text.split('\n')[1]
        if ',' in issn_isbn:
            issn_isbn = issn_isbn.split(',')
        doi = publishing_data[3].text.split('\n')[1]

        citations = self._get_citation_dynamics(paper_id)

        return (paper_name, authors, source_name, overall_citations, work_percentile, fwci,
                publishing_date, keywords, document_type, source_type, issn_isbn, doi, citations)

    # Returns list of article's authors and their affiliations
    def _get_papers_authors(self):
        authors_data_raw = self.driver.find_element(By.CLASS_NAME, 'ul--horizontal.margin-size-0').text.split('\n')

        affiliations_raw = self.driver.find_element(By.ID, 'affiliation-section'). \
            find_element(By.CLASS_NAME, 'margin-size-0').text.split('\n')

        affiliations_encoding = dict()
        for affiliation in affiliations_raw:
            words = affiliation.split(' ')
            affiliations_encoding[words[0]] = ''.join(words[1:])

        names = []
        affiliations = []
        affiliations_enc = []
        print(authors_data_raw)
        '''
        in "authors_data_raw" first entry has just the name of an author,
        and following entry has the affiliations of the previous author
        last entry does not contain author name 
        '''
        for it, author_data in enumerate(authors_data_raw):
            if it == 0:
                names.append(author_data)
            elif ';' in author_data:
                data = author_data.split('; ')
                print(data)
                names.append(data[1])
                affiliations_enc.append(data[0])
            else:
                affiliations_enc.append(author_data)
        print(dict(zip(names, affiliations_enc)))
        return dict(zip(names, affiliations_enc))

    # Parses the annual number of citations of a paper (2007-2022 so far)
    def _get_citation_dynamics(self, paper_id):
        print("Scraper " + str(id(self)) + " parses article " + str(paper_id) + "'s citation dynamics")

        citations = dict()
        url = "https://www.scopus.com/record/pubmetrics.uri?eid=2-s2.0-" + str(paper_id) + "&origin=recordpage"
        self.driver.get(url)
        # Required for dynamic elements to load
        time.sleep(2)

        year_list = self.driver.find_element(By.CLASS_NAME,
                                             'ui-selectmenu-icon.ui-icon.btn-primary.btn-icon.ico-navigate-'
                                             'down.flexDisplay.flexAlignCenter.flexJustifyCenter.flexColumn')
        # Choose the period from 2007-2022
        year_list.click()
        year = self.driver.find_element(By.ID, 'ui-id-17')
        year.click()
        show = self.driver.find_element(By.ID, 'buttonOn')
        show.click()

        dots = self.driver.find_element(By.CLASS_NAME,
                                        'highcharts-markers.highcharts-series-0.highcharts-line-'
                                        'series.highcharts-color-0.default.highcharts-tracker')
        dots = dots.find_elements(By.CLASS_NAME, 'highcharts-point.highcharts-color-0')
        for dot in dots:
            label = dot.get_attribute('aria-label').split('.')[1].split(',')
            citations[int(label[0])] = int(label[1])
        return citations
