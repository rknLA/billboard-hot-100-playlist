Charter
-------

Update Rdio playlists based on a chart.


Testing
=======

Since this is an abstraction built on top of the Rdio API,
I've decided not to mock or stub the API to make sure the tests
actually test what they should be testing.

As such, you'll need to update the `config.py` file with your
OAuth credentials, and go through the OAuth flow in the command-line.py
example to grab a valid OAuth token.  You should then update the config
with the token so that the tests can run.

You can run the tests by running `python tests` from the project root.

The tests will create and update a playlist on your Rdio account.
The test playlist will be deleted at the end of the test.

