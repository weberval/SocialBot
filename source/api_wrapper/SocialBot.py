import twitter
import random
import time
from threading import Thread
from source.api_wrapper.Logger import Logger


class SocialBot:
    """
    The SocialBot class is built on top of the twitter module.
    It restricts the functionality of the twitter module and includes logging.
    The user which is logged in is also called the authenticated user.
    """

    def __init__(self, access_info):
        """
        Check if access_info contains all necessary information to build an twitter object.
        :param access_info:
        """

        if 'consumer_key' not in access_info or not access_info['consumer_key']:
            raise ValueError('Missing consumer_key in access_info')
        elif 'consumer_secret' not in access_info or not access_info['consumer_secret']:
            raise ValueError('Missing consumer_secret in access_info')
        elif 'access_token' not in access_info or not access_info['access_token']:
            raise ValueError('Missing access_token in access_info')
        elif 'access_token_secret' not in access_info or not access_info['access_token_secret']:
            raise ValueError('Missing access_token_secret in access_info')

        if (type(access_info['consumer_key']) != str or
                type(access_info['consumer_secret']) != str or
                type(access_info['access_token']) != str or
                type(access_info['access_token_secret']) != str):
            raise ValueError('All values of the access_info dict have to be of type str.')

        self.__api = twitter.Api(
            consumer_key=access_info['consumer_key'],
            consumer_secret=access_info['consumer_secret'],
            access_token_key=access_info['access_token'],
            access_token_secret=access_info['access_token_secret']
        )

        self.overwrite_sensitive = True
        self.__logger = Logger()

        # min and max response times for tweeting at statuses out of a stream (in secs)
        self.stream_min_response_time = 10
        self.stream_max_response_time = 60

    """
    LOG:
    """

    def activate_log(self, path, name):
        """
        Activates the logging via the logger instance.
        :param path:
        :param name:
        :return:
        """

        self.__logger.activate(path, name, self.overwrite_sensitive)

    def __log(self, message):
        """
        Calls the log method of the logger instance.
        :param message:
        :return:
        """

        self.__logger.log(message)

    """
    BASIC ACTIONS:
    """

    def tweet(self, text):
        """
        Tweet a text.
        :param text:
        :return:
        """

        if not text:
            raise ValueError('Missing a tweet text')
        elif type(text) != str:
            raise ValueError('The tweet text has to be of type str. Given:', type(text))

        resp = self.__api.PostUpdate(text)

        self.__log({
            'action': 'Tweeted a text',
            'text': text,
            'response': str(resp)
        })

        return resp

    def retweet(self, tweet_id):
        """
        Retweet a tweet with id. The id can be either string or int.
        :param tweet_id:
        :return:
        """

        if not tweet_id:
            raise ValueError('Missing tweet_id')
        elif type(tweet_id) != str and type(tweet_id) != int:
            raise ValueError('Tweet_id is neither type str or int. Given: ', type(tweet_id))

        resp = self.__api.PostRetweet(tweet_id)

        self.__log({
            'action': 'Retweeted tweet with id',
            'tweet_id': str(tweet_id),
            'response': str(resp)
        })

        return resp

    def reply(self, status_id, message):

        if not status_id:
            raise ValueError('Missing a status_id')
        elif type(status_id) != str and type(status_id) != int:
            raise ValueError('Status_id is neither type str or int. Given: ', type(status_id))
        elif not message:
            raise ValueError('Missing a tweet text')
        elif type(message) != str:
            raise ValueError('The tweet text has to be of type str. Given:', type(message))

        resp = self.__api.PostUpdate(message, in_reply_to_status_id=status_id)

        self.__log({
            'action': 'Replied to a status.',
            'message': message,
            'status_id': str(status_id),
            'response': str(resp)
        })

        return resp



    def favor(self, status, status_id):
        """
        Favor a status as authenticated user.
        :return:
        """

        if not status and not status_id:
            raise ValueError('Missing a status or status_id to favor.')

        resp = self.__api.CreateFavorite(status=status, status_id=status_id)

        self.__log({
            'action': 'Favored a tweet',
            'status': str(status),
            'status_id': str(status_id),
            'response': str(resp)
        })

        return resp

    def send_dm(self, username=None, user_id=None, message=None):
        """
        Send a Direct Message to a user. If both username and user_id are not None the twitter module
        only uses the user_id.
        :param username:
        :param user_id:
        :param message:
        :return:
        """

        if not username and not user_id:
            raise ValueError('Missing a username or user_id to send a dm')
        elif (username and type(username) != str) or (user_id and (type(user_id) != str and type(user_id) != int)):
            raise ValueError('Username has to be str. User_id can be str or int. Given:', type(user_id), type(username))
        elif not message:
            raise ValueError('Missing a message to send a dm')
        elif type(message) != str:
            raise ValueError('The message has to be of type str. Given:', type(message))

        resp = self.__api.PostDirectMessage(text=message, user_id=user_id, screen_name=username, return_json=True)

        self.__log({
            'action': 'Send dm to user',
            'message': message,
            'user_id': str(user_id),
            'username': str(username),
            'response': str(resp)
        })

        return resp

    """
    SEARCH FUNCTIONS:
    """

    def search_tweet(self, term):
        """
        Search for tweets containing a specified text.
        :param term:
        :return:
        """

        if not term:
            raise ValueError('Missing a search term')
        elif type(term) != str:
            raise ValueError('Search Term has to be of type str. Given: ', type(term))

        resp = self.__api.GetSearch(term=term)

        self.__log({
            'action': 'Searched for tweets containing "' + term + '"',
            'response': str(resp)
        })

        return resp

    def search_user(self, term):
        """
        Search for a user by username.
        :param term:
        :return:
        """

        if not term:
            raise ValueError('Missing a username to search')
        elif type(term) != str:
            raise ValueError('Search Term has to be of type str. Given: ', type(term))

        resp = self.__api.GetUsersSearch(term)

        self.__log({
            'action': 'Searched for user with term "' + term + '"',
            'response': str(resp)
        })

        return resp

    """
    GET FUNCTIONS:
    """

    def get_subscriptions(self, username=None, user_id=None, count=20, page=-1):
        """
        Get subscriptions for a user. If both username and user_id are not None the twitter module
        only uses the user_id.
        :param count:
        :param page:
        :param user_id:
        :param username:
        :return:
        """

        if not username and not user_id:
            raise ValueError('Missing a username or user_id to get subscriptions')
        elif (username and type(username) != str) or (user_id and (type(user_id) != str and type(user_id) != int)):
            raise ValueError('Username has to be str. User_id can be str or int. Given:', type(user_id), type(username))

        resp = self.__api.GetSubscriptions(user_id=user_id, screen_name=username, count=count, cursor=page)

        self.__log({
            'action': 'Got subscriptions for user',
            'user_id': str(user_id),
            'username': str(username),
            'response': str(resp)
        })

        return resp

    def get_tweets(self, username=None, user_id=None):
        """
        Get tweets made by a user. If both username and user_id are not None the twitter module
        only uses the user_id.
        :param username:
        :param user_id:
        :return:
        """

        if not username and not user_id:
            raise ValueError('Missing a username or user_id to get tweets')
        elif (username and type(username) != str) or (user_id and (type(user_id) != str and type(user_id) != int)):
            raise ValueError('Username has to be str. User_id can be str or int. Given:', type(user_id), type(username))

        resp = self.__api.GetUserTimeline(user_id=user_id, screen_name=username)

        self.__log({
            'action': 'Got tweets by user',
            'user_id': str(user_id),
            'username': str(username),
            'response': str(resp)
        })

        return resp

    def get_followers(self, username=None, user_id=None, page=-1):
        """
        Get max. 200 followers for a certain user on one page.
        If both username and user_id are not None the twitter module
        only uses the user_id.
        :param page:
        :param username:
        :param user_id:
        :return:
        """

        if not username and not user_id:
            raise ValueError('Missing a username or user_id to get followers')
        elif (username and type(username) != str) or (user_id and (type(user_id) != str) and type(user_id) != int):
            raise ValueError('Username has to be str. User_id can be str or int. Given:', type(user_id), type(username))

        resp = self.__api.GetFollowersPaged(user_id=user_id, screen_name=username, cursor=page)

        self.__log({
            'action': 'Got followers for user',
            'username': str(username),
            'user_id': str(user_id),
            'page': str(page),
            'response': str(resp)
        })

        return resp

    """
    GET FUNCTIONS (FOR AUTHENTICATED USER):
    """

    def get_my_replies(self):
        """
        Gets the most recent replies for the authenticated user.
        :return:
        """
        resp = self.__api.GetReplies()

        self.__log({
            'action': 'Got replies of authenticated user',
            'response': str(resp)
        })

        return resp

    def get_my_retweets(self):
        """
        Gets the most recent retweets of tweets made by the authenticated user.
        :return:
        """

        resp = self.__api.GetRetweetsOfMe()

        self.__log({
            'action': 'Got retweets of tweets made by the authenticated user',
            'response': str(resp)
        })

        return resp

    def get_my_mentions(self):
        """
        Gets the most recent mentions of the authenticated user.
        :return:
        """

        resp = self.__api.GetMentions()

        self.__log({
            'action': 'Got mentions of the authenticated user.',
            'response': str(resp)
        })

        return resp

    """
    STREAM FUNCTIONS:
    """

    def stream(self, users=None, terms=None):
        """
        Opens a stream to spectate tweets. Has to be filtered by users and/or terms.
        Users should be as user_id.
        Both users and terms have to be an array.
        :param users:
        :param terms:
        :return:
        """
        if not users and not terms:
            raise ValueError('Missing users or terms.')
        elif (users and type(users) != list) or (terms and type(terms) != list):
            raise ValueError('Both users and terms have to be of type list/array. Given:', type(users), type(terms))

        self.__log({
            'action': 'Opened Stream',
            'users': str(users),
            'terms': str(terms)
        })

        return self.__api.GetStreamFilter(follow=users, track=terms)

    def limit_stream(self, users=None, terms=None, limit=None):
        """
        Opens a stream to spectate tweets. Has to be filtered by users and/or terms.
        Users should be as user_id.
        Both users and terms have to be an array.
        :param users:
        :param terms:
        :param limit:
        :return:
        """
        if not users and not terms:
            raise ValueError('Missing users or terms.')
        elif (users and type(users) != list) or (terms and type(terms) != list):
            raise ValueError('Both users and terms have to be of type list/array. Given:', type(users), type(terms))
        elif not limit:
            raise ValueError('Missing a limit.')
        elif limit and type(limit) != int:
            raise ValueError('Limit has to be of type int.')

        stream = self.__api.GetStreamFilter(follow=users, track=terms)
        result = []

        for item in stream:
            if len(result) < limit:
                result.append(item)
            else:
                break

        return result

    def tweet_at_stream(self, message, nth_tweet=None, users=None, terms=None, limit=None):

        if not message:
            raise ValueError('Missing a message.')
        elif message and type(message) != str:
            raise ValueError('Message has to be of type str. Given: ', type(message))
        elif not nth_tweet and nth_tweet != 0:
            raise ValueError('Missing a tweet pointer on the stream.')
        elif nth_tweet and type(nth_tweet) != int:
            raise ValueError('Nth_tweet has to be of type int. Given: ', type(nth_tweet))
        elif not users and not terms:
            raise ValueError('Missing users or terms.')
        elif (users and type(users) != list) or (terms and type(terms) != list):
            raise ValueError('Both users and terms have to be of type list/array. Given:', type(users), type(terms))
        elif not limit:
            raise ValueError('Missing a limit.')
        elif limit and type(limit) != int:
            raise ValueError('Limit has to be of type int.')
        elif limit <= nth_tweet:
            raise ValueError('nth_tweet has to be smaller than the limit.')

        thread = Thread(target=self.__tweet_at_stream_thread, args=(message, nth_tweet, users, terms, limit))
        thread.start()

        return thread

    """
    THREAD FUNCTIONS:
    """

    def __tweet_at_stream_thread(self, message, nth_tweet=None, users=None, terms=None, limit=None):

        stream = self.stream(users=users, terms=terms)

        stream_results = []
        reply_results = []

        for item in stream:
            if len(stream_results) < limit:
                print(item)
                stream_results.append(item)
            else:
                break

        if nth_tweet == -1:
            for status in stream_results:
                time.sleep(random.uniform(self.stream_min_response_time, self.stream_max_response_time))
                reply_results.append(self.reply(status['id'], message))
        elif nth_tweet != -1:
            status = stream_results[nth_tweet]
            time.sleep(random.uniform(self.stream_min_response_time, self.stream_max_response_time))
            reply_results.append(self.reply(status['id'], message))

        self.__log({
            'action': 'Tweeted at stream',
            'message': message,
            'nth_tweet': str(nth_tweet),
            'users': str(users),
            'terms': str(terms),
            'limit': str(limit),
            'response': str(reply_results)
        })

        return reply_results