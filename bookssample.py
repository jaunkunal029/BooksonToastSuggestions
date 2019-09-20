import re
from apiclient.discovery import build
import random
import time
import webbrowser
import pickle
import pprint

api_key = "AIzaSyAbDCb44y-AEKqscn4UwodlgAFxJU9BZwE"

youtube = build('youtube', 'v3', developerKey=api_key)

#     channel_id = UCSzPk0ShJD6ygdZw7HqK5QA


def get_channel_videos(channel_id):

    print('in the youtube api calling function')
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()

    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    next_page_token = None

    # use the while loop to get all the videos with the help of the pageToken
    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet',
                                           maxResults=50, pageToken=next_page_token).execute()

        videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break

    return videos


def get_total_number_of_videos(channel_id):

    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()

    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet',
                                       maxResults=50).execute()

    return res['pageInfo']['totalResults']


def generate_suggestion(videolist, choice):

    random_suggestion = {}

    # loop through each of the videos present in the videoList and use regex to extract
    # the amazon web links. Then add the video title and the respective amazon web link in our
    # suggestion dictionary
    for video in videolist:
        sample_string = (video['snippet']['description'])
        match_string = re.findall(r"https?://a+[\w.-]+/[\w.-/]+", sample_string)
        if len(match_string) > 0:
            random_suggestion[video['snippet']['title']] = match_string

    # using the random function pick one title from the dictionary and then again use the random
    # function to get a random amazon web link
    if choice == 1:
        random_title = random.choice(list(random_suggestion.keys()))
        random_amazon_link = random.choice(random_suggestion[random_title])

        return random_title, random_amazon_link

    elif choice == 2:
        random_titles = random.choices(list(random_suggestion.keys()), k=5)
        return random_titles, random_suggestion


def open_amazon_link(episode_title, web_link):

    # Use the web browser to open the amazon link in chrome
    print('Video title from which the book suggestion is picked: ', episode_title)
    time.sleep(3)
    chrome_path = r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    webbrowser.get(chrome_path).open(web_link)
    print('exiting')


def check_total_number_videos():

    # checkpoint = dict()

    with open('checkAPIList.txt', 'rb') as handle:
        checkpoint = pickle.load(handle)
    handle.close()

    total_number_of_videos = get_total_number_of_videos('UCSzPk0ShJD6ygdZw7HqK5QA')
    # print('get total number', total_number_of_videos)

    if checkpoint['prev_number_of_videos'] != total_number_of_videos:
        print('time to call youtube api')
        videolist = get_channel_videos('UCSzPk0ShJD6ygdZw7HqK5QA')
        checkpoint['Video_Details'] = videolist
        checkpoint['prev_number_of_videos'] = total_number_of_videos

        with open('checkAPIList.txt', 'wb') as handle:
            pickle.dump(checkpoint, handle)

        handle.close()


# check_total_number_videos()
if __name__ == '__main__':

    check_total_number_videos()
    checkpoint = dict()

    with open('checkAPIList.txt', 'rb') as handle:
        checkpoint = pickle.load(handle)
    handle.close()
    # print(type(checkpoint['Video_Details']))
    # random_title, random_amazon_link = generate_suggestion(checkpoint['Video_Details'])
    # open_amazon_link(random_title, random_amazon_link)

    while True:
        choice = int(input('Please press 1 for generating a book suggestion or 2 for generating a random list of '
                           'episodes titles : '))
        if choice == 1 or choice == 2:
            break

    if choice == 1:
        print('generating a random amazon link from the whole BotCast Catalogue')
        random_title, random_amazon_link = generate_suggestion(checkpoint['Video_Details'], 1)
        open_amazon_link(random_title, random_amazon_link)
    elif choice == 2:
        print('generating  a sample of 5 random episode titles')

        # pprint.pprint(generate_suggestion(checkpoint['Video_Details'], 2))
        random_titles_list, episode_link_dictionary = generate_suggestion(checkpoint['Video_Details'], 2)
        for random_video in random_titles_list:
            print(random_titles_list.index(random_video)+1, random_video)

        final_choice = int(input('Please enter a choice to generate a book suggestion from that episode: '))
        print('episode selected is : ', random_titles_list[final_choice-1])
        print('random link from that episode is :',
              random.choice(episode_link_dictionary[random_titles_list[final_choice-1]]))
        open_amazon_link(random_titles_list[final_choice-1],
                         random.choice(episode_link_dictionary[random_titles_list[final_choice-1]]))



