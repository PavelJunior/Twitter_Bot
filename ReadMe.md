# Twitter Bot
This Twitter Bot written on Python using tweepy library to access Twitter APIs.
The program search specific hashtags or words in all the tweets on Tweeter, and then
target users who wrote that tweets. You can specify search queries in table.xlsx. Also
you can choose what kind of actions you want perform for this search query. Program can
automate retweets, replies, DMs and likes. In replies and DMs you can choose message you
want to use. The Bot actions intervals set up with Tweeter policies, in order not to be
considered as spam. One user will be targeted only once.

# How to set up?
1. Download the repository to your computer
2. Create twitter developer account and create an app.
3. Change setting to be able send messages in tweeter dev account. You need to open your developer portal
Then click "App settings" on your app created in 1st step. Go to the "App permissions" and choose "Read, Write, and Direct Messages".
4. Now you need to generate tokens to make bot access you account. Go back to your developer portal
Then click "Keys and tokens" on your app created in 1st step. Then press "Regenerate" in Access Token & Secret window.
5. Now you need to put your account keys in credentials.json. You need to open file and change values to
values from you twitter dev account you created in previous step. The names of values are the same in your dev account and credentials.json.
6. Fill table.xlsx with search queries, actions and messages
7. Run programm with command "python twitter_bot.py"