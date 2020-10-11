import tweepy
import pandas
import random
import time
import json


class TwitterBot:
    NEXT_TWEET_INTERVAL_RANGE = (300, 500)
    NEXT_LIKE_INTERVAL_RANGE = (100, 250)
    NEXT_DM_INTERVAL_RANGE = (150, 300)

    SEARCH_AMOUNT = 500
    INTERVAL_TO_SAVE_TARGETED_USERS = 3600

    def __init__(self):
        credentials = json.load(open('credentials.json'))
        auth = tweepy.OAuthHandler(credentials['api_key'], credentials['api_key_secret'])
        auth.set_access_token(credentials['access_token'], credentials['access_token_secret'])
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        self.current_time = 0

        self.next_tweet_time = -1
        self.next_like_time = -1
        self.next_dm_time = -1

        self.reply_list = []
        self.retweet_list = []
        self.like_list = []
        self.dm_list = []

        self.number_of_replays_in_table = -1
        self.number_of_retweets_in_table = -1
        self.number_of_likes_in_table = -1
        self.number_of_dm_in_table = -1

        self.current_replay_in_table = -1
        self.current_retweet_in_table = -1
        self.current_likes_in_table = -1
        self.current_dm_in_table = -1

        self.dm_message = ''
        self.replay_message = ''

        self.previous_targets = []
        self.table = None

    def is_user_targeted(self, user_id):
        if user_id in self.previous_targets:
            return True
        else:
            self.previous_targets.append(user_id)
            return False

    def extract_and_read_dm_data(self, dm_rows):
        search_query = dm_rows.iloc[self.current_dm_in_table, 0]
        message = dm_rows.iloc[self.current_dm_in_table, 2]
        self.dm_list = self.api.search(q=search_query, lang="en", count=self.SEARCH_AMOUNT)
        self.dm_message = message

    def extract_and_read_reply_data(self, reply_rows):
        search_query = reply_rows.iloc[self.current_replay_in_table, 0]
        message = reply_rows.iloc[self.current_replay_in_table, 2]
        self.reply_list = self.api.search(q=search_query, lang="en", count=self.SEARCH_AMOUNT)
        self.replay_message = message

    def extract_and_read_retweet_data(self, retweet_rows):
        search_query = retweet_rows.iloc[self.current_retweet_in_table, 0]
        self.retweet_list = self.api.search(q=search_query, lang="en", count=self.SEARCH_AMOUNT)

    def extract_and_read_like_data(self, like_rows):
        search_query = like_rows.iloc[self.current_likes_in_table, 0]
        self.like_list = self.api.search(q=search_query, lang="en", count=self.SEARCH_AMOUNT)

    def get_new_dm_list(self):
        dm_rows = self.table.loc[self.table['Action'] == 'DM']
        if self.current_dm_in_table == self.number_of_dm_in_table-1:
            self.current_dm_in_table = 0
        else:
            self.current_dm_in_table += 1
        self.extract_and_read_dm_data(dm_rows)

    def get_new_reply_list(self):
        reply_rows = self.table.loc[self.table['Action'] == 'Reply']
        if self.current_replay_in_table == self.number_of_replays_in_table-1:
            self.current_replay_in_table = 0
        else:
            self.current_replay_in_table += 1
        self.extract_and_read_reply_data(reply_rows)

    def get_new_retweet_list(self):
        retweet_rows = self.table.loc[self.table['Action'] == 'Retweet']
        if self.current_retweet_in_table == self.number_of_retweets_in_table-1:
            self.current_retweet_in_table = 0
        else:
            self.current_retweet_in_table += 1
        self.extract_and_read_retweet_data(retweet_rows)

    def get_new_like_list(self):
        like_rows = self.table.loc[self.table['Action'] == 'Like']
        if self.current_likes_in_table == self.number_of_likes_in_table-1:
            self.current_likes_in_table = 0
        else:
            self.current_likes_in_table += 1
        self.extract_and_read_like_data(like_rows)

    def send_dm(self):
        try:
            if not self.dm_list:
                self.get_new_dm_list()
            tweet = self.dm_list.pop()
            if not self.is_user_targeted(tweet.user.id):
                self.send_dm()
            else:
                self.api.send_direct_message(tweet.user.id, self.dm_message)
        except tweepy.error.TweepError:
            print('User {} does not allow you to dm him'.format(tweet.user.id))
            self.send_dm()

    def reply(self):
        try:
            if not self.reply_list:
                self.get_new_reply_list()
            tweet = self.reply_list.pop()
            if not self.is_user_targeted(tweet.user.id):
                self.reply()
            else:
                username = tweet.user.screen_name
                tweet_id = tweet.id
                full_message = '@{} {}'.format(username, self.replay_message)
                self.api.update_status(full_message, tweet_id)
        except:
            print("Something went wrong in method 'reply'")
            self.reply()

    def retweet(self):
        try:
            if not self.retweet_list:
                self.get_new_retweet_list()
            tweet = self.retweet_list.pop()
            if not self.is_user_targeted(tweet.user.id):
                self.retweet()
            else:
                tweet_id = tweet.id
                self.api.retweet(tweet_id)
        except:
            print("Something went wrong in method 'retweet'")
            self.retweet()

    def like(self):
        try:
            if not self.like_list:
                self.get_new_like_list()
            tweet = self.like_list.pop()
            if not self.is_user_targeted(tweet.user.id):
                self.like()
            else:
                tweet_id = tweet.id
                self.api.create_favorite(tweet_id)
        except:
            print("Something went wrong in method 'like'")
            self.like()

    def write_previous_targets(self):
        with open('targeted_users.txt', 'w+') as f:
            for user in self.previous_targets:
                f.write('{}\n'.format(user))
            f.close()

    def start(self):
        self.table = pandas.read_excel('table.xlsx')
        with open('targeted_users.txt', 'r') as f:
            for user in f:
                self.previous_targets.append(user.strip())
            f.close()

        like_rows = self.table.loc[self.table['Action'] == 'Like']
        self.number_of_likes_in_table = like_rows.shape[0]
        if self.number_of_likes_in_table > 0:
            self.current_likes_in_table = 0
            self.extract_and_read_retweet_data(like_rows)

        retweet_rows = self.table.loc[self.table['Action'] == 'Retweet']
        self.number_of_retweets_in_table = retweet_rows.shape[0]
        if self.number_of_retweets_in_table > 0:
            self.current_retweet_in_table = 0
            self.extract_and_read_retweet_data(retweet_rows)

        reply_rows = self.table.loc[self.table['Action'] == 'Reply']
        self.number_of_replays_in_table = reply_rows.shape[0]
        if self.number_of_replays_in_table > 0:
            self.current_replay_in_table = 0
            self.extract_and_read_reply_data(reply_rows)

        dm_rows = self.table.loc[self.table['Action'] == 'DM']
        self.number_of_dm_in_table = dm_rows.shape[0]
        if self.number_of_dm_in_table > 0:
            self.current_dm_in_table = 0
            self.extract_and_read_dm_data(dm_rows)

        if self.number_of_dm_in_table > 0:
            self.next_dm_time = self.current_time + random.randint(
                self.NEXT_DM_INTERVAL_RANGE[0], self.NEXT_DM_INTERVAL_RANGE[1]
            )

        if self.number_of_retweets_in_table > 0 or self.number_of_replays_in_table > 0:
            self.next_tweet_time = self.current_time + random.randint(
                self.NEXT_TWEET_INTERVAL_RANGE[0], self.NEXT_TWEET_INTERVAL_RANGE[1]
            )

        if self.number_of_likes_in_table > 0:
            self.next_like_time = self.current_time + random.randint(
                self.NEXT_LIKE_INTERVAL_RANGE[0], self.NEXT_LIKE_INTERVAL_RANGE[1]
            )

        self.main()

    def main(self):
        while True:
            try:
                print("Current time: {}, Next tweet time: {}, Next like time: {}, Next dm time: {}". format(
                    self.current_time, self.next_tweet_time, self.next_like_time, self.next_dm_time)
                )
                if self.current_time == self.next_like_time:
                    self.like()
                    self.next_like_time += random.randint(
                        self.NEXT_LIKE_INTERVAL_RANGE[0], self.NEXT_LIKE_INTERVAL_RANGE[1]
                    )

                if self.current_time == self.next_dm_time:
                    self.send_dm()
                    self.next_dm_time += random.randint(
                        self.NEXT_DM_INTERVAL_RANGE[0], self.NEXT_DM_INTERVAL_RANGE[1]
                    )

                if self.current_time == self.next_tweet_time:
                    if random.randint(0, 1) == 0 and self.number_of_replays_in_table > 0:
                        self.reply()
                    elif self.number_of_retweets_in_table > 0:
                        self.retweet()
                    self.next_tweet_time += random.randint(
                        self.NEXT_TWEET_INTERVAL_RANGE[0], self.NEXT_TWEET_INTERVAL_RANGE[1]
                    )

                if self.current_time % self.INTERVAL_TO_SAVE_TARGETED_USERS == 0 and self.current_time != 0:
                    self.write_previous_targets()

                self.current_time += 1
                time.sleep(1)
            except KeyboardInterrupt:
                exit()
            except:
                print("Something went wrong in method 'main'")


if __name__ == "__main__":
    TwitterBot().start()




