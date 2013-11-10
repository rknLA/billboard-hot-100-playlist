from lxml import html
from lxml.cssselect import CSSSelector
import re
import urllib2

scraped_keys = []

base_url = 'http://www.billboard.com'

ChartItemSelector = CSSSelector('article.chart_albumTrack_detail')
PlayLinkSelector = CSSSelector('.options > li > ul > li > a')
ChartPositionSelector = CSSSelector('.chart_position')
NextLinkSelector = CSSSelector('div.chart_pager_bottom > div.item-list > ul.pager > li.last > a')

TrackKeyRE = re.compile(r'tid=(.\d+)&')

def scrapeBillboard():
  global scraped_keys
  scrapeChartPage(base_url + '/charts/hot-100')
  keys = scraped_keys
  # reset scraped keys in case this gets called twice in one run
  scraped_keys = []
  return keys

def scrapeChartPage(url):
  tree = html.parse(url)
  root = tree.getroot()
  chart_item_nodes = ChartItemSelector(root)

  for node in chart_item_nodes:
    chart_position_text = ChartPositionSelector(node)[0].text
    chart_position = int(chart_position_text)
    play_links = PlayLinkSelector(node)
    for link in play_links:
      if link.text.strip() == 'Rdio':
        href = link.attrib['href']
        re_match = TrackKeyRE.search(href)
        if re_match is not None:
          track_key = re_match.groups()[0]
          scraped_keys.insert(chart_position, track_key)
        else:
          # most likely this track isn't available on rdio
          print 'skipping track %d' % (chart_position,)

  next_link = NextLinkSelector(root)
  if len(next_link) == 1:
    uri = next_link[0].attrib['href']
    scrapeChartPage(base_url + uri)

if __name__ == '__main__':
  scrapeBillboard()
