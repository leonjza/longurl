#!/usr/bin/env python

# longurl.py ShortURL Expander
#
# 2013 Leon Jacobs
# Licensed under IDC (I don't Care) license.

import sys
import httplib
from urlparse import urlparse
from urlparse import urlunsplit

# valid redirect codes to follow. They _should_ present a Location header
redirect_codes = [ 301, 302, 307, 308 ]

# protocols that we support. This is all HTTPLib gets anyways
schemes = [ "http", "https" ]

# command line argument check
if len(sys.argv) is not 2:
  print "[!] Invalid number of arguments. Expecting longurl.py 'http://someurl.io'"
  sys.exit(1)

request = sys.argv[1]
o = urlparse(request)

# we need _at least_ a netloc and scheme.
try:
   assert all([o.scheme, o.netloc]) , "Invalid Url: %r" % request
except AssertionError as e:
   print e
   sys.exit(1)

# check that we got a valid scheme
if o.scheme not in schemes:
   print "%r is not a valid protocol for this tool" % o.scheme
   sys.exit(1)

# function to process a url and follow the redirects
def expand_url(o, request, previous_request = None):

    print "[*] Next stop: %r" % request 

    # check that we have a valid netloc, else we try get one from the previous request. We want full URL's for output
    if not o.netloc:
      previous_request = urlparse(previous_request)
      if previous_request.netloc:
        request = urlunsplit([previous_request.scheme, previous_request.netloc, o.path, "", "",])
        o = urlparse(request)

    # http? https?
    if "https" in o.scheme:
       conn = httplib.HTTPSConnection(o.netloc, timeout=10)
    else:
       conn = httplib.HTTPConnection(o.netloc, timeout=10)

    # request o.path and record the response
    conn.putrequest("GET", o.path, None)
    conn.putheader("User-Agent", "longurl.py - ShortURL Expander")
    conn.endheaders()
    response = conn.getresponse()

    print "[*] Got status: %s with reason: %s" %(response.status, response.reason)

    # did we get a redirect code?
    if response.status in redirect_codes:

        # check if we got a location header
        if "None" in response.getheader("Location"):

            print "[!] Had a redirect code, but got no location..."
            sys.exit(1)

        expand_url(urlparse(response.getheader("Location")), response.getheader("Location"), request)

    else:
      print "\n[*] The final looks to be: %r" % request

    # end the recursion
    return

if __name__ == "__main__":
    expand_url(o, request)
