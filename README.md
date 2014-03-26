Suicide Watch
=============

**FORKED FROM th3o6a1d (github.com/th3o6a1d/suicide_watch)**

Twitter mining for suicide prevention, gun violence, influenza, and other public
 health threats. Wordlist obtained from Argyle et al. "Tracking Suicide Risk
 Factors Through Twitter in the US." Crisis 2014; Vol. 35(1):51–59.

Opens twitter public stream. Identifies concerning tweets by sets of keywords.
 Once it flags a tweet, it will get the location listed by the user and also
 attempt to reverse geocode the user's address using the Google Maps API.  It
 will then filter the tweet based on the locations given.  For filtered tweets,
 it will then scan that user's past tweets, tally up instances of the sets of
 keywords, record the number of followers, and dump the output in txt and json
 formats.

Uses TwitterAPI for Python.  To install, pip install TwitterAPI.  
