#!/bin/bash

echo -e "------------------------------------------------ Micro-Crawler Start---------------------------------------------"

fb_worker="fb_worker"
instareddit_worker="instareddit_worker"
twitter_worker="twitter_worker"
linkedin_worker="linkedin_worker"
generic_worker="generic_worker"
news_worker="news_worker"
super_worker="super_worker"
start_app="start app"
youtube_worker="youtube_worker"
avatar="avatar_worker"



fbworker="celery -A task_queue worker -n fb_worker -c 1 -Q fb_queue --loglevel=info"
instaredditworker="celery -A task_queue worker -n instareddit_worker -c 1 -Q instareddit_queue --loglevel=info"
twitterworker="celery -A task_queue worker -n twitter_worker -Q twitter_queue -c 1 --loglevel=info"
linkedinworker="celery -A task_queue worker -n linkedin_worker  -c 1  -Q linkedin_queue --loglevel=info"
genericworker="celery -A task_queue worker -n generic_worker -Q generic_queue -c 1 --loglevel=info"
youtubeworker="celery -A task_queue worker -n youtube_worker -Q youtube_queue --loglevel=info"
newsworker="celery -A task_queue worker -n news_worker -Q news_queue --loglevel=info"
superworker="celery -A task_queue worker -n super_worker --loglevel=info"
startapp="python app.py"
avatar_queue="celery -A task_queue worker -n avatar_worker -Q avatar_queue --loglevel=info"


gnome-terminal --tab --title="$fb_worker" --command="bash -c 'echo -----------waiting for workers --------------; $fbworker;  $SHELL '" \
               --tab --title="$twitter_worker" --command="bash -c 'echo worker starting; $twitterworker; $SHELL'" \
               --tab --title="$instareddit_worker" --command="bash -c 'echo worker starting; $instaredditworker; $SHELL'" \
               --tab --title="$linkedin_worker" --command="bash -c 'echo worker starting; $linkedinworker; $SHELL'" \
               --tab --title="$generic_worker" --command="bash -c 'echo worker starting; $genericworker; $SHELL'" \
               --tab --title="$super_worker" --command="bash -c 'echo worker starting; $superworker; $SHELL'" \
               --tab --title="$start_app" --command="bash -c 'echo app start; $startapp; $SHELL'" \
               --tab --title="$youtube_worker" --command="bash -c 'echo worker start; $youtubeworker; $SHELL'" \
               --tab --title="$avatar_worker" --command="bash -c 'echo worker start; $avatar_queue; $SHELL'" \
               --tab --title="$news_worker" --command="bash -c 'echo worker starting; $newsworker; $SHELL'" 

