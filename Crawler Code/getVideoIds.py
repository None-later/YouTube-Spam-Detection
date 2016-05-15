#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import datetime as dt

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = ["AIzaSyABDLbZVLdQIiEkbHCffNnK4cXA-xDBeEQ","AIzaSyBhErLc8toAd3f0OgOg-WjV1gonI1FrrfM"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(adate,bdate):
  x = 0
  while(x == 0):
    for keys in DEVELOPER_KEY:
        try:
          youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=keys)
          x = 1
          break
        except:
          if(keys == DEVELOPER_KEY[-1]):
            sleep(5)
            x = 0
  #print adate,bdate
  search_response = youtube.search().list(
      part="id",
      maxResults=50,
      order="date",
      publishedAfter=adate,
      publishedBefore=bdate,
      regionCode="US",
      type="video",
      fields="items/id,nextPageToken",
      videoCategoryId="25"
    ).execute()

  #print search_response
  #exit()
  currPageToken=""
  while("nextPageToken" in search_response.keys()):
    #print currPageToken
    for search_result in search_response.get("items", []):
      print search_result["id"]["videoId"]
    currPageToken=search_response["nextPageToken"]
    search_response = youtube.search().list(
      part="id",
      maxResults=50,
      pageToken=currPageToken,
      order="date",
      publishedAfter=adate,
      publishedBefore=bdate,
      regionCode="US",
      type="video",     
      fields="items/id,nextPageToken",
      videoCategoryId="25"
    ).execute() 
  for search_result in search_response.get("items", []):
    print search_result["id"]["videoId"] # to be stored in output

#call this as file_name.py > result.txt
if __name__ == "__main__":
  final_date=dt.datetime(2016,05,6,00,00,00)
  curr_date=dt.datetime(2016,04,25,00,00,00)
  try:
    while(curr_date!=final_date):
      next_date=curr_date+dt.timedelta(hours=1)
      youtube_search(curr_date.strftime('%Y-%m-%dT%H:%M:%SZ'),next_date.strftime('%Y-%m-%dT%H:%M:%SZ'))
      curr_date=next_date
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
