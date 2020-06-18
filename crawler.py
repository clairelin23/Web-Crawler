import urllib.request
import urllib.parse
import urllib.robotparser
import bs4
import re

def visit_url(url):
    try:
        with urllib.request.urlopen(url) as url_file:
            bytes = url_file.read()
    except urllib.error.URLError as url_err:
        print(f'Error opening url: {url}\n{url_err}')
    else:
        soup = bs4.BeautifulSoup(bytes, 'html.parser')
        text = soup.get_text()
        absolute_links = {urllib.parse.urljoin(url, anchor.get('href', None))
                      for anchor in soup('a')}
        return text, absolute_links

def ok_to_crawl(url):
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.scheme or not parsed_url.hostname:
        print('Not a valid absolute url: ', url)
        return False
    # Build the corresponding robots.txt url name
    robot = urllib.parse.urljoin(f'{parsed_url.scheme}://{parsed_url.netloc}',
                                 '/robots.txt')
    print(parsed_url.scheme)
    print(parsed_url.netloc)
    user_agent = urllib.request.URLopener.version  # our user-agent
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robot)
    try:
        rp.read()
    except urllib.error.URLError as url_err:
        print(f'Error opening robot.txt for url {robot}\n{url_err}')
        return False
    else:
        return rp.can_fetch(user_agent, url)

def crawl(seed, search_term):
    to_crawl = {seed}
    visited = set()
    interesting_urls = set()
    url_count = 0

    while to_crawl and url_count <= 30:  # limit crawling to 30 urls.
        # pop an element in tocrawl list, order dont metter
        url = to_crawl.pop()
        # check last 3 elem of string, skip pdf and jpg
        if url[-3:] not in ('pdf', 'jpg'):
            if url not in visited:
                visited.add(url)
                if ok_to_crawl(url):
                    result = visit_url(url)
                    if result is not None:
                        text, new_urls = result
                        to_crawl = to_crawl | new_urls
                        url_count += 1
                        # Allow plural form - may not always work.
                        match = re.search(fr'(\b{search_term}s?\b)',text,
                                          re.IGNORECASE)
                        if match is not None:
                            interesting_urls.add(url)
    return interesting_urls

def main():
    seed = 'http://sjsu.edu/'
    search_term = 'spartan'
    urls_of_interest = crawl(seed, search_term)
    for each_url in urls_of_interest:
        print(each_url)

if __name__ == '__main__':
    main()