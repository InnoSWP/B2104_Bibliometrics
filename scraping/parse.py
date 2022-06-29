import ast

from elsapy.elsclient import *
from elsapy.elsdoc import *
from elsapy.elssearch import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class Scraper:

    def __init__(self):
        with open('scraping/key.txt', 'r') as file:
            key = file.readline()
        self.client = ElsClient(key)
        self.papers = None
        self.authors = dict()
        self.quartiles = pd.read_excel('data/quartiles.xlsb',
                                       sheet_name=1, engine='pyxlsb')
        print('Scraper', id(self), 'was created')

    # Starts parsing all papers, then (based on papers) parses all authors
    def parse(self, file_id):
        print('Scraper', id(self), 'began parsing')
        self.papers = self._get_papers()

        paper_ids = list(self.papers['id'])
        author_ids = self._parse_papers(paper_ids, file_id)

        with open('data/authors_list.txt', 'w') as file:
            for item in list(author_ids):
                file.write("%s\n" % item)
        # Based on data on Innopolis papers, parse their metrics
        self._parse_authors(author_ids, file_id)
        self._parse_disciplines(file_id)

    # Web scrape ResearchGate for authors photos
    @staticmethod
    def _parse_disciplines(file_id):
        information = list()
        path = "chromedriver.exe"
        options = Options()
        options.headless = False
        driver = webdriver.Chrome(path, options=options)
        driver.implicitly_wait(5)
        # Iterate over pages with university workers' data
        for page in range(1, 9):
            print('Parsing page #' + str(page) + '/9')

            url = 'https://www.researchgate.net/institution/Innopolis-University/members/' + str(page)
            driver.get(url)
            members = driver.find_element(By.CLASS_NAME,
                                          'nova-legacy-o-stack.nova-legacy-o-stack--gutter-xl.nova-legacy-o-stack--spacing-none.nova-legacy-o-stack--show-divider.nova-legacy-o-stack--no-gutter-outside')
            members = members.find_elements(By.XPATH, "*")
            for num, member in enumerate(members):
                print(str(num + 1) + '/' + str(len(members)))

                author = dict()
                author_data = member.find_elements(By.XPATH, "*")[0]. \
                    find_elements(By.XPATH, "*")[0]. \
                    find_elements(By.XPATH, "*")

                author['photo_link'] = author_data[0].find_element(By.XPATH, "*"). \
                    find_element(By.XPATH, "*").get_attribute('src')
                if 'default' in author['photo_link']:
                    author['photo_link'] = None
                text_data = author_data[1].find_element(By.XPATH, "*").find_elements(By.XPATH, "*")

                author['name'] = text_data[0].text
                author['department'] = 'No department'
                author['disciplines'] = []

                for it in range(1, len(text_data)):
                    text = text_data[it].find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
                    author[text[0].text.lower()] = text[1].text

                    if text[0].text.lower() == 'disciplines':
                        disciplines = text[1].find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
                        author['disciplines'] = list([discipline.text for discipline in disciplines])
                information.append(author)

        with open('data/authors_add_static.json', 'r') as static_json:
            authors_static = json.load(static_json)

        information += authors_static
        with open("data/authors_add_" + str(file_id) + ".json", "w") as outfile:
            json.dump(information, outfile)

    # Iterate over (Innopolis) authors and get data on them
    def _parse_authors(self, author_ids, file_id):
        overall = str(len(author_ids))
        for it, author_id in enumerate(author_ids):
            print('Processing author #' + str(it + 1) + '/' + overall)
            self.authors[author_id] = self._get_author_by_id(author_id)

        with open("data/authors_" + str(file_id) + ".json", "w") as outfile:
            json.dump(self.authors, outfile)
        return self.authors

    # Iterate over (Innopolis affiliated) papers and get their data
    # file_format can be equal to any of: ['csv', 'json']
    def _parse_papers(self, paper_ids, file_id, file_format='json'):
        print('Scraper', id(self), 'began parsing publications')
        author_ids = set()  # Contains scopus IDs of all authors, who have at least one work, affiliated in Innopolis
        paper_authors_affils_data = dict()
        papers_citations = dict()
        overall_it = len(paper_ids)
        # Collect data on papers
        for it, paper_id in enumerate(paper_ids):
            print('Parsing article #', it + 1, 'out of', overall_it)
            paper_authors_affils_data[paper_id], innopolis_authors = self._get_paper_affils(paper_id)
            author_ids |= innopolis_authors
            papers_citations[paper_id] = self._get_paper_citations(paper_id)

        paper_affils_df = pd.DataFrame.from_dict({'id': paper_authors_affils_data.keys(),
                                                  'authors_affils': paper_authors_affils_data.values()})
        paper_citations_df = pd.DataFrame.from_dict({'id': papers_citations.keys(),
                                                     'citations': papers_citations.values()})

        paper_add_data = pd.merge(paper_affils_df, paper_citations_df, on='id', how="left")
        self.papers = pd.merge(self.papers, paper_add_data, on='id', how="left")

        if file_format == 'csv':
            self.papers.to_csv('data/papers_' + str(file_id) + '.csv', index=False)  # Cache the data
        else:
            json_data = self.papers.set_index('id').to_json(orient="index")
            json_data = json.loads(json_data)
            with open("data/papers_" + str(file_id) + ".json", "w") as outfile:
                json.dump(json_data, outfile)
        return author_ids

    # Returns the pair:
    # dict (author_id) -> ([affil_name])
    # set of authors, affiliated in Innopolis
    def _get_paper_affils(self, scopus_id):
        print('Scraper', id(self), 'parses document', str(scopus_id))
        paper = AbsDoc(scp_id=str(scopus_id))  # Get general information on the paper
        paper.read(self.client)
        authors_response = paper.data['authors']['author']

        affils_names = dict()
        affils_responses = paper.data['affiliation']
        if isinstance(affils_responses, dict):
            affils_responses = [affils_responses]
        # Parse the affiliations of an article
        for affils_response in affils_responses:
            affils_names[affils_response['@id']] = affils_response['affilname']

        author_affils = dict()
        # When parsing papers, we select authors, affiliated at Innopolis, to later provide detailed statistics on them
        innopolis_affiliated = set()
        for author_response in authors_response:
            # Some authors may not have affiliation in the paper,
            # in this case it is replaced by their current affiliation
            if 'affiliation' not in author_response:
                author_current_affil = self._get_author_current_affil(author_response['@auid'])
                # Some authors may not have affiliation at all
                if author_current_affil not in affils_names:
                    continue
                if 'innopolis' in affils_names[author_current_affil].lower():
                    innopolis_affiliated.add(author_response['@auid'])
                continue
            else:
                affils = author_response['affiliation']

            if not isinstance(affils, list):
                affils = [affils]
            author_affils[author_response['@auid']] = {'affils': list(), 'name': ''}
            for affil in affils:
                author_affils[author_response['@auid']]['affils'].append(affils_names[affil['@id']])
                author_affils[author_response['@auid']]['name'] = author_response['ce:indexed-name']
                if 'innopolis' in affils_names[affil['@id']].lower():
                    innopolis_affiliated.add(author_response['@auid'])

        return author_affils, innopolis_affiliated

    # Returns a dict with papers' citations over years: (year_str) -> (citations number)
    def _get_paper_citations(self, paper_id):
        print('Scraper', id(self), 'parses document', str(paper_id), 'citations')

        citation_data = self.client.exec_request('https://api.elsevier.com/content/abstract/citations/?scopus_id=' +
                                                 str(paper_id) + '&date=2015-2022')
        citations = dict()

        for i in range(0, len(
                citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader']['columnTotal'])):
            citation_number = \
                citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader']['columnTotal'][
                    i]['$']
            if int(citation_number) > 0:
                year = citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader'][
                    'columnHeading'][i]['$']
                citations[year] = int(citation_number)

        return citations

    # Given Scopus ID of a researcher, returns his or her metrics
    def _get_author_by_id(self, scopus_id):
        print('Scraper', id(self), 'parses author', str(scopus_id))
        author = self.client.exec_request('https://api.elsevier.com/content/author/author_id/' + str(scopus_id))[
            'author-retrieval-response'][0]
        # If no researcher was found by id, return None
        if author['@status'] != 'found':
            print('Author', scopus_id, 'was not found')
            return None

        author_data = dict()  # Contains author's metrics
        author_data['name'] = author['author-profile']['preferred-name']['given-name'] + " " + \
                              author['author-profile']['preferred-name']['surname']
        author_data['overall_citations'] = author['coredata']['citation-count']
        affils = author['author-profile']['affiliation-current']['affiliation']
        if not isinstance(affils, list):
            affils = [affils]
        author_data['institution'] = list()  # An author may simultaneously be affiliated in two or more universities
        for affil in affils:
            if 'afdispname' in affil['ip-doc']:
                author_data['institution'].append(affil['ip-doc']['afdispname'])  # Add affiliation names to the list

        papers_search = ElsSearch('AU-ID(' + scopus_id + ')', 'scopus')
        papers_search.execute(self.client, True)  # Get all papers, published by researcher
        author_papers_ids = papers_search.results_df['dc:identifier'].apply(lambda x: x.split(':')[1]).tolist()
        papers_years_list = papers_search.results_df['prism:coverDate'].apply(lambda x: str(x).split('-')[0]).tolist()

        author_data['hirsch_ind'] = self.client.exec_request(
            'https://api.elsevier.com/content/author/author_id/' + str(scopus_id) + '?view=METRICS')[
            'author-retrieval-response'][0]['h-index']

        author_data['inno_affil_citations'], author_data['papers_published'] = \
            self._get_author_dynamics(scopus_id, author_papers_ids, papers_years_list)
        author_data['paper_id'] = author_papers_ids
        author_data['publishing_period'] = str(min(papers_years_list)) + "-" + str(max(papers_years_list))

        return author_data

    # Get work dynamic of a selected author
    # Returns two dicts (year) -> (amount)
    # First dict is the citations over years, second - number of papers published
    def _get_author_dynamics(self, scopus_id, author_papers_ids, papers_years_list):
        citations = {str(year): 0 for year in range(2010, 2022)}
        published = {str(year): 0 for year in range(2010, 2022)}

        overall = str(len(author_papers_ids))
        for it, author_papers_id in enumerate(author_papers_ids):
            print('Processing article ' + str(author_papers_id) + ' #' + str(it + 1) + '/' + overall + ' for author',
                  scopus_id)

            if papers_years_list[it] not in published:
                published[papers_years_list[it]] = 0
            published[papers_years_list[it]] += 1
            paper_dataframe = self.papers[self.papers['id'] == int(author_papers_id)]
            # Current paper was not affiliated in Innopolis
            if paper_dataframe.empty:
                continue
            # .iloc[0] as dataframe may not contain more than one record for a paper
            paper_cite = paper_dataframe.iloc[0]['citations']
            # During compression to csv, some data types may have been distorted (dict stored as str)
            if type(paper_cite) == str:
                paper_cite = ast.literal_eval(paper_cite)
            # Iterate over years, in which the paper was cited
            for year in paper_cite.keys():
                if year not in citations:
                    citations[year] = 0
                citations[year] += paper_cite[year]
        return citations, published

    # Given Scopus ID of a researcher, returns current affiliation of the researcher
    def _get_author_current_affil(self, scopus_id):
        author_affil = self.client. \
            exec_request('https://api.elsevier.com/content/author/author_id/' + str(scopus_id))[
            'author-retrieval-response'][0]
        return author_affil['affiliation-current']['@id']

    # Get a quartile of a source by its Scopus ID
    def _get_quartile(self, source_id):
        if source_id == 'NaN':
            return -1
        # Non-indexed source
        if source_id not in self.quartiles['Scopus Source ID'].values:
            return -1
        quartiles = self.quartiles.loc[self.quartiles['Scopus Source ID'] == source_id]['Quartile'].tolist()
        return max(quartiles)

    # Requests a DataFrame of all papers with affiliation in Innopolis
    def _get_papers(self):
        print('Scraper', id(self), 'parses list of all documents')
        # Get list of all documents with at least one affiliation in IU
        papers_response = ElsSearch("affil(Innopolis University)", 'scopus')
        papers_response.execute(self.client, True)
        papers = papers_response.results_df
        # Drop unusable data
        papers = papers.drop(['@_fa', 'link', 'prism:url', 'eid', 'openaccess',
                              'openaccessFlag', 'prism:volume', 'prism:pageRange',
                              'subtype', 'pii', 'freetoread', 'freetoreadLabel',
                              'prism:issn', 'prism:isbn', 'prism:eIssn',
                              'prism:coverDisplayDate', 'pubmed-id', 'article-number',
                              'prism:issueIdentifier', 'dc:creator', 'affiliation'],
                             axis=1)
        papers = papers.rename(columns={"dc:identifier": "id", "dc:title": "title",
                                        "prism:publicationName": "publisher",
                                        "prism:coverDate": "publication_date", "prism:doi": "doi",
                                        "citedby-count": "overall_citations",
                                        "prism:aggregationType": "source_type",
                                        "subtypeDescription": "work_type"})
        # ID comes in format SC:1123581321
        papers['id'] = papers['id'].apply(lambda x: x.split(':')[1])
        papers['publication_date'] = papers['publication_date'].apply(lambda x: str(x).split(' ')[0])
        papers['source-id'] = papers['source-id'].apply(lambda x:
                                                        'Nan' if pd.isnull(x) else str(int(x)))
        # Cache the data
        papers.to_csv('data/papers_raw.csv', index=False)
        return papers
