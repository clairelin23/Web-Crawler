# ----------------------------------------------------------------------
# Name:        homework9
# Purpose:     Practice with Beautiful Soup and urllib
#
# Author(s): Alora Clem and Claire Lin
# Team Name: Slytherin
# ----------------------------------------------------------------------
"""
Practice with Beautiful Soup and urllib

Compiles COVID-19 information from multiple Wikipedia web pages and
saves that information in a text file on the user's computer
"""
import urllib.request
import urllib.parse
import urllib.robotparser
import bs4
import re

def visit_url(url, search_term):
    """
    Gets the country name, total cases, death cases, and url to retreive
    1st paragragh from a Wikipedia page
    :param url: (string) the Wikipedia page
    :param search_term: (string) the string contained in country's name
    :return: a list of tutple conataining country name, total cases,
    death cases, and url to retreive 1st paragragh
    """
    try:
        with urllib.request.urlopen(url) as url_file:
            bytes = url_file.read()
    except urllib.error.URLError as url_err:
        print(f'Error opening url: {url}\n{url_err}')
    else:
        soup = bs4.BeautifulSoup(bytes, 'html.parser')
        table = soup.find('table', id = 'thetable')
        rows = table.find_all('tr')
        country_row =[]
        for row in rows:
            link = row.find('a')
            if link:
                match = re.search(search_term, link.get_text(), re.IGNORECASE)
                if match:
                    country_name = link.get_text()
                    country_link = link.get('href', None)
                    stats = row.find_all('td')
                    try:
                        cases = stats[0].get_text().strip('\n').replace(',', ''
                                                                        )
                        death = stats[1].get_text().strip('\n').replace(',', ''
                                                                        )
                        country_row.append((country_name, country_link, cases,
                                            death))
                    except IndexError:
                        print('cannot find cases or death')
    return country_row

def get_population(search_term, url):
    """
    Gets the population of a country in Wikipedia page
    :param search_term: (string) the country whose population we are
    interested
    :param url: (string) the Wikipedia page
    :return: population of the country
    """
    try:
        with urllib.request.urlopen(url) as url_file:
            bytes = url_file.read()
    except urllib.error.URLError as url_err:
        print(f'Error opening url: {url}\n{url_err}')
    else:
        soup = bs4.BeautifulSoup(bytes, 'html.parser')
        table = soup('table')[0]
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            link = row.find('a')
            if link:
                match = re.search(search_term, link.get_text(), re.IGNORECASE)
                if match:
                    stats = row.find_all('td')
                    if stats[2]:
                        pop = stats[2].get_text().strip('\n').replace(',', '')
                        return pop

        print('cannot find population')
        return None

def get_paragraph(url):
    """
    Gets the 1st paragrgh from given Wikipedia url
    :param url: (string) absolute Wikipedia url
    :return: the 1st paragraph, None if no 1st paragrgh found
    """
    full_url = urllib.parse.urljoin('https://en.wikipedia.org',url)
    try:
        with urllib.request.urlopen(full_url) as url_file:
            bytes = url_file.read()
    except urllib.error.URLError as url_err:
        print(f'Error opening url: {full_url}\n{url_err}')
    else:
        soup = bs4.BeautifulSoup(bytes, 'html.parser')
        regex = re.compile(r'\S', re.IGNORECASE)
        paragraph = soup.find_all('p')
        for p in paragraph:
            if re.match(regex, p.get_text()):
                return p.get_text()
        return None

def crawl(seed, seed2, search_term):
    """
    Crawl the wikipedia pages and find desired info
    :param seed: (string) absolute url
    :param seed2: (string) absolute url to get total population
    :param search_term: (string) the term we are looking in the urls
    """
    stats = visit_url(seed, search_term)
    if stats:
        # create (overwite) an output file
        open(search_term.lower() + 'summary.txt', 'w',
             encoding='utf-8').close()
        for the_tuple in stats:
            write_to_file(the_tuple, search_term, seed2)
    else:
        print('No country found!')

def write_to_file(the_tuple,search_term,seed2):
    """
    Get the total population from the another wikipedia page and format
    the strings to output to a file
    :param tuple: (string) the tuple containing country name, total
    cases, death cases, and url to retreive 1st paragragh
    :param seed2: (string) absolute url to get total population
    :param search_term: (string) the term we are looking in the urls
    """
    country, url, case_total, death_total = the_tuple
    pop = int(get_population(country,seed2))
    paragraph = get_paragraph(url)
    case_total = int(case_total)
    death_total = int(death_total)
    case_per = case_total/ (pop/100000)
    death_per = death_total/ (pop/100000)
    format_tot_d = f'{death_total:,}'
    format_tot_c = f'{case_total:,}'
    format_d = f'{death_per:,.1f}'
    format_c = f'{case_per:,.1f}'
    format_p = f'{pop:,}'
    # strings to help formatting below
    l_one = "Country: "
    l_two = "Population:"
    l_three = "Total confirmed cases:"
    l_four = "Total Deaths:"
    l_five = "Cases per 100,000 people:"
    l_six = "Deaths per 100,000 people:"
    long = len(l_six)
    with open(search_term.lower() + 'summary.txt', 'a', encoding='utf-8') \
            as output_file:
        output_file.write(
            f'{l_one}{country}\n'
            f'{l_two}{format_p:>{long - len(l_two) + 15}}\n'
            f'{l_three}{format_tot_c:>{long - len(l_three) + 15}}\n'
            f'{l_four}{format_tot_d:>{long - len(l_four) + 15}}\n'
            f'{l_five}{format_c:>{long - len(l_five) + 17}}\n'
            f'{l_six}{format_d:>17}\n'
            f'{paragraph}\n')

def main():
    base = 'https://en.wikipedia.org/'
    seed = base + 'wiki/2019-20_coronavirus_pandemic_by_country_and_territory'
    seed2 = base + 'wiki/List_of_countries_and_dependencies_by_population'
    search_term = input("Please enter a search term: ")
    crawl(seed, seed2, search_term)

if __name__ == '__main__':
    main()