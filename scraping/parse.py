import pandas as pd
from ElsapyCustom.elsclient import *
from ElsapyCustom.elsprofile import *
from ElsapyCustom.elssearch import *
from ElsapyCustom.elsdoc import *


class Scraper:
    def __init__(self):
        with open('scraping/key.txt', 'r') as file:
            key = file.readline()
        self.client = ElsClient(key)

    def parse(self, preload=True):
        print('Scraper', id(self), 'began parsing')
        if preload:
            papers = pd.read_csv('data/papers.csv')
        else:
            papers = self._get_papers()
        paper_ids = list(papers['id'])
        author_ids = set()
        paper_authors_affils_data = dict()
        papers_citations = dict()
        overall_it = len(paper_ids)
        for it, paper_id in enumerate(paper_ids):
            print('Parsing article #', it + 1, 'out of', overall_it)
            paper_authors_affils_data[paper_id], innopolis_authors = self._get_paper_affils(paper_id)
            author_ids |= innopolis_authors
            papers_citations[paper_id] = self._get_paper_citations(paper_id)
        paper_affils_df = pd.DataFrame.from_dict({'id': paper_authors_affils_data.keys(),
                                                  'authors_affils': paper_authors_affils_data.values()})

        papers = pd.merge(papers, paper_affils_df, on='id', how="left")
        papers.to_csv('data/new_papers.csv', index=False)

        haha = 0

        authors = dict()
        for author_id in author_ids:
            authors[author_id] = self._get_author_by_id(author_id)

        return papers, paper_authors_affils_data, authors

    def _get_paper_affils(self, scopus_id):
        print('Scraper', id(self), 'parses document', str(scopus_id))
        paper = AbsDoc(scp_id=str(scopus_id))
        paper.read(self.client)
        authors_response = paper.data['authors']['author']

        affils_names = dict()
        affils_responses = paper.data['affiliation']
        if isinstance(affils_responses, dict):
            affils_responses = [affils_responses]

        for affils_response in affils_responses:
            affils_names[affils_response['@id']] = affils_response['affilname']

        author_affils = dict()
        innopolis_affiliated = set()
        for response in authors_response:
            affils = response['affiliation']
            if not isinstance(affils, list):
                affils = [affils]
            author_affils[response['@auid']] = list()
            for affil in affils:
                author_affils[response['@auid']].append(affils_names[affil['@id']])
                if affil['@id'] == '60105869':
                    innopolis_affiliated.add(response['@auid'])

        # if len(innopolis_affiliated) == 0:
        #     pass
        #     # Do not actually know what to do in this case
        return author_affils, innopolis_affiliated

    def _get_paper_citations(self, paper_id):
        citation_data = self.client.exec_request('https://api.elsevier.com/content/abstract/citations/?scopus_id=' +
                                                 str(paper_id) + '&date=2000-2022')
        citations = dict()

        for i in range(0, len(
                citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader']['columnTotal'])):

            if int(citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader']['columnTotal'][
                       i]['$']) > 0:
                citations[citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader'][
                    'columnHeading'][i]['$']] = \
                    citation_data['abstract-citations-response']['citeColumnTotalXML']['citeCountHeader'][
                        'columnTotal'][i][
                        '$']

        return citations

    def _get_author_by_id(self, scopus_id):
        author = self.client.exec_request('https://api.elsevier.com/content/author/author_id/' + str(scopus_id))
        return author

    def _get_university_info(self):
        info = ElsAffil(affil_id='60105869')
        info.read(self.client)
        return info

    def _get_papers(self):
        print('Scraper', id(self), 'parses list of all documents')
        papers_response = ElsSearch("affil(Innopolis University)", 'scopus')
        papers_response.execute(self.client, True)
        papers = papers_response.results_df
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
        papers['id'] = papers['id'].apply(lambda x: x.split(':')[1])
        papers['source-id'] = papers['source-id'].apply(lambda x:
                                                        'Nan' if pd.isnull(x) else str(int(x)))

        papers.to_csv('data/papers.csv', index=False)
        return papers
