from lxml import html
from lxml.cssselect import CSSSelector
import re
import urllib2

scraped_keys = []

base_url = 'http://www.billboard.com'

ChartLinkSelector = CSSSelector('.field-content > a')

ChartTitleSelector = CSSSelector('#page-title')
ChartItemSelector = CSSSelector('article.chart_albumTrack_detail')
ChartItemNameSelector = CSSSelector('header > h1')
ChartItemArtistSelector = CSSSelector('header > p > a')
ChartItemArtistFallbackSelector = CSSSelector('header > p')
PlayLinkSelector = CSSSelector('.options > li > ul > li > a')
ChartPositionSelector = CSSSelector('.chart_position')
NextLinkSelector = CSSSelector('div.chart_pager_bottom > div.item-list > ul.pager > li.last > a')


TrackKeyRE = re.compile(r'tid=(.\d+)&')

def chartList():
  charts = []
  tree = html.parse(base_url + '/charts')
  root = tree.getroot()

  chart_links = ChartLinkSelector(root)

  for chart in chart_links:
    uri = chart.attrib['href']
    chart = {
      'title': chart.text,
      'billboard_url': base_url + uri,
      'path': uri[8:] # extract /charts/
    }
    charts.append(chart)

  return charts

def scrapeChart(chart_uri):
  chart_url = base_url + '/charts/' + chart_uri
  keys = []
  metadata = []
  scrapeChartPage(chart_url, keys, metadata)

  tree = html.parse(chart_url)
  root = tree.getroot()
  title_nodes = ChartTitleSelector(root)
  if title_nodes is None or len(title_nodes) != 1:
    return None
  title = title_nodes[0].text

  return {'title': title,
          'keys': keys,
          'metadata': metadata}

def scrapeChartPage(url, outKeys, outMetadata):
  tree = html.parse(url)
  root = tree.getroot()
  chart_item_nodes = ChartItemSelector(root)

  for node in chart_item_nodes:
    chart_position_text = ChartPositionSelector(node)[0].text
    chart_position = int(chart_position_text)
    track_name = ChartItemNameSelector(node)[0].text

    artist_content = ChartItemArtistSelector(node)
    if len(artist_content) == 0:
      artist_content = ChartItemArtistFallbackSelector(node)
    artist = artist_content[0].text
    play_links = PlayLinkSelector(node)
    for link in play_links:
      if link.text.strip() == 'Rdio':
        href = link.attrib['href']
        re_match = TrackKeyRE.search(href)
        if re_match is not None:
          track_key = re_match.groups()[0]
          outKeys.insert(chart_position, track_key)
          outMetadata.insert(chart_position, {'name': track_name,
                                              'artist': artist})
        else:
          # most likely this track isn't available on rdio
          print 'skipping track %d' % (chart_position,)

  next_link = NextLinkSelector(root)
  if len(next_link) == 1:
    uri = next_link[0].attrib['href']
    scrapeChartPage(base_url + uri, outKeys, outMetadata)

if __name__ == '__main__':
  scrapeBillboard()
