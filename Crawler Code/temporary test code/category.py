import gdata.youtube
import gdata.youtube.service
def PrintVideoFeed(feed):
    for entry in feed.entry:
    	PrintEntryDetails(entry)
def S():
    yt_service = gdata.youtube.service.YouTubeService() 
    # Turn on HTTPS/SSL access.
    # Note: SSL is not available at this time for uploads.
    #yt_service.developer_key="AI39si6vZgiEMMdOV2LdtCmWSVecmK0hC-StbAr3Zb2Bj_Nl4ZH6cbAooWBdwh0pqJvtdXjGn2xvg4G8C4pXiVgPWBCtgN9efw"
    #yt_service.ssl = True
    entry = yt_service.GetYouTubeVideoEntry(video_id='RzMlrlQn6zg')
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.orderby = 'viewCount'
    query.racy = 'include'
    query.categories.append("news")
    # for search_term in list_of_search_terms:
    #   new_term = search_term.lower()
    #   query.categories.append('/%s' % new_term)
    feed = yt_service.YouTubeQuery(query)
    PrintVideoFeed(feed)

if __name__ == '__main__':
    S()
