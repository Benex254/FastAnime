from html.parser import HTMLParser
import os
from kivy.storage.jsonstore import JsonStore
from collections import deque
import threading
from time import sleep
from View.components import MediaCard
from pytube import YouTube
from kivy.loader import _ThreadPool 
from kivy.clock import Clock
from kivy.cache import Cache


Cache.register("anime")

"""
gotta learn how this works :)
"""
# class _Worker(Thread):
#     def __init__(self, pool, tasks):
#         Thread.__init__(self)
#         self.tasks = tasks
#         self.daemon = True
#         self.pool = pool
#         self.start()

#     def run(self):
#         while self.pool.running:
#             func, args, kwargs = self.tasks.get()
#             try:
#                 func(*args, **kwargs)
#             except Exception as e:
#                 print(e)
#             self.tasks.task_done()

# class _ThreadPool(object):
#     '''Pool of threads consuming tasks from a queue
#     '''
#     def __init__(self, num_threads):
#         super(_ThreadPool, self).__init__()
#         self.running = True
#         self.tasks = queue.Queue()
#         for _ in range(num_threads):
#             _Worker(self, self.tasks)

#     def add_task(self, func, *args, **kargs):
#         '''Add a task to the queue
#         '''
#         self.tasks.put((func, args, kargs))

#     def stop(self):
#         self.running = False
#         self.tasks.join()

user_data = JsonStore("user_data.json")
my_list = user_data.get("my_list")["list"] # returns a list of anime ids
yt_stream_links = user_data.get("yt_stream_links")["links"]

if yt_stream_links:
    for link in yt_stream_links:
        Cache.append("anime",link[0],tuple(link[1]))

# for youtube video links gotten from from pytube which is blocking
class MediaCardDataLoader(object):
    def __init__(self):
        self._resume_cond = threading.Condition()
        self._num_workers = 5
        self._max_upload_per_frame = 5
        self._paused = False
        self._q_load = deque()
        self._q_done = deque()
        self._client = []
        self._running = False
        self._start_wanted = False
        self._trigger_update = Clock.create_trigger(self._update)
    def start(self):
        '''Start the loader thread/process.'''
        self._running = True

    def run(self, *largs):
        '''Main loop for the loader.'''
        pass

    def stop(self):
        '''Stop the loader thread/process.'''
        self._running = False

    def pause(self):
        '''Pause the loader, can be useful during interactions.

        .. versionadded:: 1.6.0
        '''
        self._paused = True

    def resume(self):
        '''Resume the loader, after a :meth:`pause`.

        .. versionadded:: 1.6.0
        '''
        self._paused = False
        self._resume_cond.acquire()
        self._resume_cond.notify_all()
        self._resume_cond.release()

    def _wait_for_resume(self):
        while self._running and self._paused:
            self._resume_cond.acquire()
            self._resume_cond.wait(0.25)
            self._resume_cond.release()

    def cached_fetch_data(self,yt_watch_url):
        data:tuple = Cache.get("anime",yt_watch_url) # type: ignore # trailer_url is the yt_watch_link
        if not data[0]:
            yt = YouTube(yt_watch_url)
            preview_image = yt.thumbnail_url 
            try:
                video_stream_url = yt.streams.filter(progressive=True,file_extension="mp4")[-1].url
                # sleep(0.5)
                data = preview_image,video_stream_url
                yt_stream_links.append((yt_watch_url,data))
                user_data.put("yt_stream_links",links=yt_stream_links)
            except:
                data = preview_image,None
        return data

    def _load(self, kwargs):
        while len(self._q_done) >= (
                self._max_upload_per_frame * self._num_workers):
            sleep(0.1) # type: ignore
        self._wait_for_resume()
        yt_watch_link = kwargs['yt_watch_link']
        try:
            data = self.cached_fetch_data(yt_watch_link)
            print("Update: ",data)
        except Exception as e:
            data = None
            print(f"Not accesible:{e} ")

        self._q_done.appendleft((yt_watch_link, data))
        self._trigger_update()
    def _update(self,*largs):
        if self._start_wanted:
            if not self._running:
                self.start()
            self._start_wanted = False

        # in pause mode, don't unqueue anything.
        if self._paused:
            self._trigger_update()
            return

        for _ in range(self._max_upload_per_frame):
            try:
                yt_watch_link, data= self._q_done.pop()
            except IndexError:
                return
                    # update client
            for c_yt_watch_link, client in self._client[:]:
                if yt_watch_link != c_yt_watch_link:
                    continue

                # got one client to update
                if data:
                    # client.set_preview_image(data[0])
                    trailer_url = data[1]
                    print(trailer_url,"-----------------")
                    if trailer_url:
                        client.set_trailer_url(trailer_url)
                        print(client.title,self._running)
                        Cache.append("anime",yt_watch_link,data)
                self._client.remove((c_yt_watch_link, client))
                    
        self._trigger_update()

    def media_card(self,anime_item,load_callback=None, post_callback=None,
              **kwargs):

        media_card = MediaCard()
        media_card.anime_id = anime_item["id"]
        if anime_item["title"]["english"]:
            media_card.title =  anime_item["title"]["english"]
        else:
            media_card.title =  anime_item["title"]["romaji"]
        # if anime_item.get("cover_image"):
        media_card.cover_image_url =  anime_item["coverImage"]["medium"]
        media_card.popularity =  str(anime_item["popularity"])
        media_card.favourites =  str(anime_item["favourites"])
        media_card.episodes =  str(anime_item["episodes"])
        if anime_item.get("description"):
            media_card.description =  anime_item["description"]
        media_card.first_aired_on =  f'{anime_item["startDate"]["day"]}-{anime_item["startDate"]["month"]}-{anime_item["startDate"]["year"]}'
        media_card.studios =  ", ".join([studio["name"] for studio in anime_item["studios"]["nodes"]])
        if anime_item.get("tags"):
            media_card.tags =  ", ".join([tag["name"] for tag in anime_item["tags"]])
        media_card.media_status =  anime_item["status"]
        if anime_item.get("genres"):
            media_card.genres = ",".join(anime_item["genres"])
        # media_card.characters = 
        if anime_item["id"] in my_list:
            media_card.is_in_my_list = True
        if anime_item["averageScore"]:
            stars = int(anime_item["averageScore"]/100*6)
            if stars:
                for i in range(stars):
                    media_card.stars[i] = 1

        if anime_item["trailer"]:
            yt_watch_link = "https://youtube.com/watch?v="+anime_item["trailer"]["id"]
            data = Cache.get("anime",yt_watch_link) # type: ignore # trailer_url is the yt_watch_link
            if data:
                if data[1] not in (None,False): 
                    media_card.set_preview_image(data[0])
                    media_card.set_trailer_url(data[1])
                    return media_card
            else:
                # if data is None, this is really the first time
                self._client.append((yt_watch_link,media_card))
                self._q_load.appendleft({
                    'yt_watch_link': yt_watch_link,
                    'load_callback': load_callback,
                    'post_callback': post_callback,
                    'current_anime':anime_item["id"],
                    'kwargs': kwargs})
                if not kwargs.get('nocache', False):
                    Cache.append('anime',yt_watch_link, (False,False))
                self._start_wanted = True
                self._trigger_update()
        return media_card

    
class LoaderThreadPool(MediaCardDataLoader):
    def __init__(self):
        super(LoaderThreadPool, self).__init__()
        self.pool:_ThreadPool|None = None

    def start(self):
        super(LoaderThreadPool, self).start()
        self.pool = _ThreadPool(self._num_workers)
        Clock.schedule_interval(self.run, 0)

    def stop(self):
        super(LoaderThreadPool, self).stop()
        Clock.unschedule(self.run)
        self.pool.stop()

    def run(self, *largs):
        while self._running:
            try:
                parameters = self._q_load.pop()
            except:
                return
            self.pool.add_task(self._load, parameters)

MediaCardLoader = LoaderThreadPool()
# Logger.info('Loader: using a thread pool of {} workers'.format(
    # Loader.num_workers))