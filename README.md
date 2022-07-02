<p align="center">
    <a href="https://github.com/InnoSWP/B2104_Bibliometrics" alt="Contributors">
        <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=green" /></a>
    <a href="https://github.com/InnoSWP/B2104_Bibliometrics" alt="Contributors">
        <img src="https://img.shields.io/static/v1?label=python&message=3.x&color=blue" /></a>
</p>

# Bibliometrics API

This product uses web-scraping to provide an API to easily extract data from Elsveir (Scopus) database. 

## Table of contents
- [How to install?](#Installation)
- [What features are available?](#Features)
- [What datasource we use?](#Databases)
- [Demonstration of the API](#Demo) 
- [Contribution](#Contribution)
- [License](#License)

## Installation
### Requirements
This product requires:
- Python 3.x
- [Pandas](https://pandas.pydata.org) v1.3.5+ 
- [Elsapy](https://github.com/ElsevierDev/elsapy) v0.5.0+
- [Selenium](https://www.selenium.dev) v4.2.0+
- [Django](https://www.djangoproject.com)

You can use requirements.txt to install all the dependencies:

```sh
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```
You would also need an API key for Elsevier API which you can get from [Elsevier Developer Portal](https://dev.elsevier.com/).
For scraper to work correctly, that key should provide access to Citations Overview API.
Key should be put into scraper/key.txt file. Please also make sure that Elsevier API is accessible from your IP-address. 

## Features
Parse Scopus database for the following metrics:
- Citation count and dynamics of an author
- List of papers, affiliated at selected institution
- For a selected paper - citation dynamics, authors and their affiliations.

### Sources
This product fetches data about citation counts and affiliations from Scopus database. 
Quartile data is pre-fetched from Scopus CiteScore

## Demo
You can see the demo of the product [here](https://drive.google.com/file/d/1zsY_d5nisFahe05f3yoVIECK7anDIS3U/view).

## Contribution
You can help to develop this software by creating issues on GitHub or by making pull requests.
## License
This software is distributed under The MIT License.
