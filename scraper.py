DATABASE_NAME = 'data.sqlite'

import os
os.environ['SCRAPERWIKI_DATABASE_NAME'] = DATABASE_NAME

import scraperwiki
import lxml.html
import urlparse
from pprint import pprint

result_schema = {
        'rank': None,
        'bib': None,
        'fis_code': None,
        'name': None,
        'year_of_birth': None,
        'nation': None,
        'run_1': None,
        'run_2': None,
        'total_time': None,
        'diff': None,
        'fis_points': None,
}

# generator of FIS race links
def race_link_results(url):
    html = scraperwiki.scrape(url)
    root = lxml.html.fromstring(html)
    result_table = root.cssselect("table.fisfootable")[0]
    status_cells = result_table.cssselect("td.status")
    for status_cell in status_cells:
        result_div = status_cell.cssselect("div")[0]
        for element, attribute, link, pos in result_div.iterlinks():
            event_page = scraperwiki.scrape(link)
            event_root = lxml.html.fromstring(event_page)
            event_rows = event_root.cssselect("table.footable tbody tr")
            for event_row in event_rows:
                last_cell = event_row.cssselect("td:last-child")[0]
                for race_links in last_cell.iterlinks():
                    print get_cell_value(event_row.cssselect("td")[2], "span a")
                    extra = {
                        'date': get_cell_value(event_row.cssselect("td")[1], "span a"),
                        'place': get_cell_value(event_row.cssselect("td")[2], "span a"),
                        'country': get_cell_value(event_row.cssselect("td")[3], "a span"),
                        'codex': get_cell_value(event_row.cssselect("td")[4], "a"),
                        'discipline': get_cell_value(event_row.cssselect("td")[5], "a"),
                    }
                    yield (race_links[2], extra)

def get_cell_value(element, css):
    return element.cssselect(css)[0].text_content()

FIS_URL = "http://data.fis-ski.com/cross-country/results.html"
for link, raceinfo in race_link_results(FIS_URL):
    html = scraperwiki.scrape(link)
    root = lxml.html.fromstring(html)
    result_table = root.cssselect("table.footable")[0]
    result_cells = result_table.cssselect("tr")
    for result_cell in result_cells:
        athlete = result_cell.cssselect("td")[1]
        print get_cell_value(athlete, "")
        athlete_url = athlete.cssselect("a")[0].get("href")
        parsed = urlparse.urlparse(athlete_url)
        athlete_id = urlparse.parse_qs(parsed.query)['competitorid']
        result = {
            'event': raceinfo['codex'],
            'rank': result_cell.cssselect("td")[0].text_content(),
            'athlete': get_cell_value(result_cell.cssselect("td")[1], "a"),
            'competitor_id': athlete_id,
            'yob': result_cell.cssselect("td")[2].text_content(),
            'nation': result_cell.cssselect("td")[3].text_content(),
            'time': result_cell.cssselect("td")[4].text_content(),
            'behind': result_cell.cssselect("td")[5].text_content(),
            'points': result_cell.cssselect("td")[6].text_content()
        }
        print result
    print link
    print raceinfo['date']
    scraperwiki.sqlite.save(unique_keys=['codex'], data=raceinfo, table_name="data")

# # Write out to the sqlite database using scraperwiki library
# data = {"name": "susan", "occupation": "software developer"}
# scraperwiki.sqlite.save(unique_keys=['name'], data=data, table_name="data")
# 
# An arbitrary query against the database
# pprint(scraperwiki.sql.select("* from data where 'name'='susan'"))
