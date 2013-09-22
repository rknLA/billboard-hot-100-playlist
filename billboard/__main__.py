if __name__ == '__main__':
  from charter.charter import Charter
  import config
  from rdio.rdio import Rdio
  from scraper import scrapeBillboard

  rdio = Rdio((config.RDIO_CONSUMER_KEY, config.RDIO_CONSUMER_SECRET),
              config.RDIO_TEST_OAUTH_TOKEN)
  charter = Charter(rdio=rdio)
  new_chart = scrapeBillboard()
  charter.updatePlaylist('p6354244', new_chart)
  
