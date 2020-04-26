
import praw
class auth_reddit:
    def __init__(self):
        self.client_id=""
        self.client_secret=""
        self.user_agent='by u/ravisng_h'
        
    def get(self):
        reddit = praw.Reddit(client_id=self.client_id,
                             client_secret=self.client_secret,
                             user_agent=self.user_agent)
        return reddit
        
