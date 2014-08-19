if __name__ == '__main__':
  from charter.charter import Charter
  import config
  from rdio.rdio import Rdio
  import scraper

  rdio = Rdio((config.RDIO_CONSUMER_KEY, config.RDIO_CONSUMER_SECRET),
              config.RDIO_TEST_OAUTH_TOKEN)
  charter = Charter(rdio=rdio)

  scraper.chartList()
  new_chart = scraper.scrapeChart('http://www.billboard.com/charts/hot-100')
  charter.updatePlaylist('my playlist key', new_chart)
  
