# rScraper
A Scraper for Reddit that does not use the official API. Instead it scrapes data using Python's [requests](https://github.com/psf/requests) library.  
Following types of data can be scraped:  

* Popular Posts
* Subreddits  
* Users  
* Smart Search -- Users and Subreddits  
* Search -- Subreddits and Posts

## Getting Started  
* Getting this repository:  
  ```bash
  mkdir rScraper
  cd rScraper
  git init
  git add .
  git remote add origin https://www.github.com/saadejazz/rScraper
  ```
* Installing dependencies:  
  ```bash
  python -m pip install requests bs4 datetime
  ```
  
## Usage  
* Scrape popular posts against categories, countries, and time period.  

  **Code:**  
  
  ```python
  from rScraper.rScraper import popularPosts

  results = popularPosts(category = "top", timePeriod = "All Time")
  # another variant
  # all possible categories are: "hot"(country as sub-category), "top"(timePeriod as subcategory), "new", "rising".
  # results = popularPosts(category = "hot", country = "United Kingdom")
  print(results)
  ```
  
  **Output:**  
  
  ```python
  [{'poster': {'author_id': 't2_816cd',
     'username': 'SrGrafo',
     'link': 'https://www.reddit.com/user/SrGrafo'},
    'post_id': 't3_ccr8c8',
    'post_link': 'https://www.reddit.com/r/gaming/comments/ccr8c8/take_your_time_you_got_this/',
    'is_posted_by_moderator': False,
    'timestamp': '2019-07-13 16:28:13',
    'subreddit': {'id': 't5_2qh03',
     'name': 'gaming',
     'link': 'https://www.reddit.com/r/gaming'},
    'categories': [],
    'is_promoted': False,
    'text': 'Take your time, you got this',
    'media': 'https://i.redd.it/5ugttvttk3a31.jpg',
    'statistics': {'upvote_ratio': 0.98,
     'num_comments': 3636,
     'num_crossposts': 103,
     'score': 268697}},
   {'poster': {'author_id': 't2_fc0l0',
     'username': 'reddit_exchanges',
     'link': 'https://www.reddit.com/user/reddit_exchanges'},
    'post_id': 't3_g79xhz',
    'post_link': 'https://www.reddit.com/user/reddit_exchanges/comments/g79xhz/reddit_gifts_stay_at_home_series_sign_up_before/',
    'is_posted_by_moderator': False,
    'timestamp': '2020-04-24 15:03:14',
    'subreddit': {'id': '', 'name': '', 'link': ''},
    'categories': [],
    'is_promoted': True,
    'text': 'Reddit Gifts Stay At Home Series! Sign up before May 11th!',
    'media': 'https://external-preview.redd.it/oFhaygtv9HRbVljOpnUso-4fOITxyTtQbiUQgr5B31k.jpg?auto=webp&s=d0d3fd2f734014b6c075eb325ff5b30db3dbeb04',
    'statistics': {'upvote_ratio': 0.12,
     'num_comments': 0,
     'num_crossposts': 0,
     'score': 0}},....]
  ```
  **Note:** All possible values of *country* and *timePeriod* are in the file *codes.py*.  

* Scrape a subreddit. 

  **Code:**  
  
  ```python
  from rScraper.rScraper import subreddit

  results = subreddit(subreddit = "westworld", category = "hot")
  print(results)
  ```
  **Output:**  
  
  ```python
  {'id': 't5_2xhxq',
   'name': 'westworld',
   'url': 'https://www.reddit.com/r/westworld/',
   'category': '',
   'type': 'public',
   'description': 'Subreddit for the HBO series Westworld.',
   'num_subscribers': 757138,
   'currently_active': 4866,
   'timestamp_created': '2013-06-08 23:50:58',
   'icon_media_directory': 'https://b.thumbs.redditmedia.com/YHkaogTL3ZYfztRSnxzb25y5Rhq4L0VXWeArjpHNr4w.png',
   'num_moderators': 12,
   'top_moderators': [{'name': 'Space-Dementia',
     'link': 'https://www.reddit.com/user/Space-Dementia'},
    {'name': 'NicholasCajun',
     'link': 'https://www.reddit.com/user/NicholasCajun'},
    {'name': 'JoyousCacophony',
     'link': 'https://www.reddit.com/user/JoyousCacophony'},
    {'name': 'SimplifyEUW', 'link': 'https://www.reddit.com/user/SimplifyEUW'},
    {'name': 'MarcoHanYT', 'link': 'https://www.reddit.com/user/MarcoHanYT'},
    {'name': 'mcmahoniel', 'link': 'https://www.reddit.com/user/mcmahoniel'},
    {'name': 'Hypohamish', 'link': 'https://www.reddit.com/user/Hypohamish'},
    {'name': 'Noerdy', 'link': 'https://www.reddit.com/user/Noerdy'},
    {'name': 'Plainchant', 'link': 'https://www.reddit.com/user/Plainchant'},
    {'name': 'CyaInTheSkies',
     'link': 'https://www.reddit.com/user/CyaInTheSkies'}],
   'posts': [{'poster': {'author_id': 't2_9qf0f',
      'username': 'NicholasCajun',
      'link': 'https://www.reddit.com/user/NicholasCajun'},
     'post_id': 't3_gb6yhq',
     'post_link': 'https://www.reddit.com/r/westworld/comments/gb6yhq/westworld_3x08_crisis_theory_postepisode/',
     'is_posted_by_moderator': True,
     'timestamp': '2020-05-04 02:16:07',
     'subreddit': {'id': 't5_2xhxq',
      'name': 'westworld',
      'link': 'https://www.reddit.com/r/westworld'},
     'categories': [],
     'is_promoted': False,
     'text': 'Westworld - 3x08 "Crisis Theory" - Post-Episode Discussion',
     'media': '',
     'statistics': {'upvote_ratio': 0.95,
      'num_comments': 5619,
      'num_crossposts': 0,
      'score': 960}},...]}
  ```
* Scrape User data.  

  **Code:**

  ```python
  from rScraper.rScraper import user

  result = user(username = "greyWormShark", category = "top", timePeriod = "This Month")
  print(result)
  ```

  **Output:**

  ```python
  {'id': 't2_6dcbrdfy',
   'profile_id': 't5_2mq8ru',
   'username': 'greyWormShark',
   'url': 'https://www.reddit.com/user/greyWormShark/',
   'description': '',
   'icon_media_directory': 'https://www.redditstatic.com/avatars/avatar_default_07_A5A4A4.png',
   'timestamp_created': '2020-05-03 15:32:19',
   'karma_points': {'comment_karma': 0, 'post_karma': 1},
   'subscribers': 0,
   'custom_feeds': [],
   'subreddits': [],
   'posts': []}
  ```
  
* Smart Search to reveal picture, and id against a username.  

  **Code:**  

  ```python
  from rScraper.rScraper import smartSearch

  user = smartSearch(username = "greyWormShark")
  subreddit = smartSearch(subreddit = "greysanatomy")
  print(user, "\n", subreddit)
  ```

  **Output:**  

  ```python
  ## for user: 
  {'id': 't2_6dcbrdfy',
   'username': 'greyWormShark',
   'url': 'https://www.reddit.com/user/greyWormShark/',
   'media_directory': 'https://www.redditstatic.com/avatars/avatar_default_07_A5A4A4.png'}
  ## for subreddit:
  {'id': 't5_2t2vo',
   'username': 'greysanatomy',
   'url': 'https://www.reddit.com/r/greysanatomy/',
   'media_directory': 'https://b.thumbs.redditmedia.com/ss0L-8MRW23gOdqu_hEAqs7MgGLZgE3j4N-ur4eRK7A.png'}
  ```

* Search for subreddits and posts. (no search available for users except smart search)  

  **Code:**  

  ```python
  from rScraper.rScraper import search

  results = search("westworld", entityType = "communities")
  ## other variant
  ## results = search("westworld", entityType = "posts")
  print(results)
  ```

  **Output:**  

  ```python
  [{'id': 't5_2xhxq',
    'username': 'westworld',
    'url': 'https://www.reddit.com/r/westworld/',
    'icon_media_directory': 'https://b.thumbs.redditmedia.com/YHkaogTL3ZYfztRSnxzb25y5Rhq4L0VXWeArjpHNr4w.png',
    'num_subscribers': 757149,
    'type': 'public'},
   {'id': 't5_2ulbr',
    'username': 'funkopop',
    'url': 'https://www.reddit.com/r/funkopop/',
    'icon_media_directory': 'https://b.thumbs.redditmedia.com/I5_t9ZlCrUAWUS_IGCeuS1zC7jmcNYL0JKV0lpIh6_Q.png',
    'num_subscribers': 130283,
    'type': 'public'},
   {'id': 't5_2qh5b',
    'username': 'philosophy',
    'url': 'https://www.reddit.com/r/philosophy/',
    'icon_media_directory': 'https://styles.redditmedia.com/t5_2qh5b/styles/communityIcon_jj94dz6qi3v31.png',
    'num_subscribers': 14672371,
    'type': 'public'},....]
  ```




