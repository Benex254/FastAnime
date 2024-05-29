import os
import time
import json
import re
import shutil

from subprocess import Popen, run, PIPE
from fuzzywuzzy import fuzz

broken_link_pattern = r"https://tools.fast4speed.rsvp/\w*"

def path_parser(path:str)->str:
    return path.replace(":","").replace("/", "").replace("\\","").replace("\"","").replace("'","").replace("<","").replace(">","").replace("|","").replace("?","").replace(".","").replace("*","")

# TODO: WRITE Docs for each method
class AnimdlApi:
    @classmethod
    def run_animdl_command(cls,cmds:list,capture = True):
        if py_path:=shutil.which("python"):    
            if capture:
                return run([py_path,"-m", "animdl", *cmds],capture_output=True,stdin=PIPE,text=True)
            else:
                return run([py_path,"-m", "animdl", *cmds])

    @classmethod
    def run_custom_command(cls,cmds:list[str])->Popen|None:
        """
        Runs an AnimDl custom command with the full power of animdl and returns a subprocess(popen) for full control
        """
# Todo: add a parserr function 
        # TODO: parse the commands
        parsed_cmds = list(cmds)

        if py_path:=shutil.which("python"): 
            base_cmds = [py_path,"-m","animdl"]
            cmds_ = [*base_cmds,*parsed_cmds]
            child_process = Popen(cmds_)
            return child_process
        else:
            return None
        
    @classmethod
    def stream_anime_by_title(cls,title,episodes_range=None)->Popen|None:
        anime = cls.get_anime_url_by_title(title)
        if not anime:
            return None
# Todo: shift to run custom animdl cmd
        if py_path:=shutil.which("python"): 
            base_cmds = [py_path,"-m", "animdl","stream",anime[1]]   
            cmd = [*base_cmds,"-r",episodes_range] if episodes_range else base_cmds
            streaming_child_process = Popen(cmd)
            return streaming_child_process

    @classmethod
    def download_anime_by_title(cls,title,on_episode_download_progress,on_complete,output_path,episodes_range:str|None=None,quality:str="best"):
# TODO: add on download episode complete 
        data = cls.get_stream_urls_by_anime_title(title,episodes_range)
        if not data:
            return None,None
        failed_downloads = []
        successful_downloads = []
        anime_title,episodes_to_download = data
        anime_title:str = anime_title.capitalize()
        
        if not episodes_to_download:
            return False,None
        
        # determine download location

        parsed_anime_title = path_parser(anime_title)

        download_location = os.path.join(output_path,parsed_anime_title)
        if not os.path.exists(download_location):
            os.mkdir(download_location)
# TODO: use a generator that gives already filtered by quality streams
        for episode in episodes_to_download:
            episode_number = episode["episode"]
            episode_title = f"Episode {episode_number}"
            try:
                streams = episode["streams"]

                # remove the brocken streams
# TODO: make the filter broken streams a global internal method
                filter_broken_stream = lambda stream: True if not re.match(broken_link_pattern,stream.get("stream_url")) else False
                streams = list(filter(filter_broken_stream,streams))

                # get the appropriate stream or default to best
                get_quality_func = lambda stream_: stream_.get("quality") if stream_.get("quality") else 0
                quality_args = quality.split("/")
                if quality_args[0] == "best":
                    stream=max(streams,key=get_quality_func)
                elif quality_args[0] == "worst":
                    stream=min(streams,key=get_quality_func)
                else:
                    success = False
                    try:
                        for stream_ in streams:
                            if str(stream_.get("quality")) == quality_args[0]:
                                if stream_url_:=stream.get("stream_url"):
                                    stream = stream_url_
                                    success=True  
                                    break
                        if not success:
                            if quality_args[1] == "worst":
                                stream=min(streams,key=get_quality_func)
                            else:
                                stream=max(streams,key=get_quality_func)
                    except Exception as e:
                        stream=max(streams,key=get_quality_func)
                        
                # determine episode_title
                if title:=stream.get("title"):
                    episode_title = f"{episode_title} - {path_parser(title)}"
                    
                parsed_episode_title = episode_title.replace(":","").replace("/", "").replace("\\","")
                episode_download_location = os.path.join(download_location,parsed_episode_title)
                if not os.path.exists(episode_download_location):
                    os.mkdir(episode_download_location)

                stream_url = stream.get("stream_url")
                audio_tracks = stream.get("audio_tracks")
                subtitles = stream.get("subtitle")

                episode_info = {
                    "episode":parsed_episode_title,
                    "anime_title": anime_title
                }

                # check if its adaptive or progressive and call the appropriate downloader
                if stream_url and subtitles and audio_tracks:
                    cls.download_adaptive(stream_url,audio_tracks[0],subtitles[0],episode_download_location,on_episode_download_progress,episode_info)
                elif stream_url and subtitles:
                    # probably wont occur
                    cls.download_video_and_subtitles(stream_url,subtitles[0],episode_download_location,on_episode_download_progress,episode_info)
                else:
                    cls.download_progressive(stream_url,episode_download_location,episode_info,on_episode_download_progress)

                successful_downloads.append(episode_number)
            except:
                failed_downloads.append(episode_number)
        on_complete(successful_downloads,failed_downloads,anime_title)

    @classmethod
    def download_with_mpv(cls,url,output_path,on_progress):
        if mpv:=shutil.which("mpv"):
            process = Popen([mpv,url,f"--stream-dump={output_path}"],stderr=PIPE,text=True,stdout=PIPE)
            progress_regex = re.compile(r"\d+/\d+") # eg Dumping 2044776/125359745

            for stream in process.stderr: # type: ignore
                if matches:=progress_regex.findall(stream):
                    current_bytes,total_bytes = [float(val) for val in matches[0].split("/")]
                    on_progress(current_bytes,total_bytes)
            return process.returncode
        else:
            return False

    @classmethod
    def download_adaptive(cls,video_url,audio_url,sub_url,output_path,on_progress,episode_info):
        on_progress_ = lambda current_bytes,total_bytes: on_progress(current_bytes,total_bytes,episode_info)
        episode = episode_info.get("anime_title") + " - " + episode_info.get("episode").replace(" - ","; ")
        sub_filename = episode + ".ass"
        sub_filepath = os.path.join(output_path,sub_filename)
        is_sub_failure = cls.download_with_mpv(sub_url,sub_filepath,on_progress_)

        audio_filename = episode + ".mp3"
        audio_filepath = os.path.join(output_path,audio_filename)
        is_audio_failure = cls.download_with_mpv(audio_url,audio_filepath,on_progress_)

        video_filename = episode + ".mp4"
        video_filepath = os.path.join(output_path,video_filename)
        is_video_failure = cls.download_with_mpv(video_url,video_filepath,on_progress_)

        if is_video_failure:
            raise Exception
                    
    @classmethod
    def download_video_and_subtitles(cls,video_url,sub_url,output_path,on_progress,episode_info):
        on_progress_ = lambda current_bytes,total_bytes: on_progress(current_bytes,total_bytes,episode_info)
        episode = episode_info.get("anime_title") + " - " + episode_info.get("episode").replace(" - ","; ")
        sub_filename = episode + ".ass"
        sub_filepath = os.path.join(output_path,sub_filename)
        is_sub_failure = cls.download_with_mpv(sub_url,sub_filepath,on_progress_)
        
        video_filename = episode + ".mp4"
        video_filepath = os.path.join(output_path,video_filename)
        is_video_failure = cls.download_with_mpv(video_url,video_filepath,on_progress_)

        if is_video_failure:
            raise Exception

    @classmethod
    def download_progressive(cls,video_url,output_path,episode_info,on_progress):
        episode = episode_info.get("anime_title") + " - " + episode_info.get("episode").replace(" - ","; ")
        file_name = episode + ".mp4"
        download_location = os.path.join(output_path,file_name)
        on_progress_ = lambda current_bytes,total_bytes: on_progress(current_bytes,total_bytes,episode_info)
        isfailure = cls.download_with_mpv(video_url,download_location,on_progress_)
        if isfailure:
            raise Exception
                   
    @classmethod
    def get_anime_match(cls,anime_item,title):
        return fuzz.ratio(title,anime_item[0])
    
    @classmethod
    def get_anime_url_by_title(cls,title:str):
# TODO: rename to animdl anime url
        result = cls.run_animdl_command(["search",title])
        possible_animes = cls.output_parser(result)
        if possible_animes:
            anime = max(possible_animes.items(),key=lambda anime_item:cls.get_anime_match(anime_item,title))
            return anime # ("title","anime url")
# TODO: make it raise animdl anime url not found exception
        return None
    
    @classmethod
    def get_stream_urls_by_anime_url(cls,anime_url:str,episodes_range=None):
        if not anime_url:
            return None
        try:
            cmd = ["grab",anime_url,"-r",episodes_range] if episodes_range else ["grab",anime_url] 
            result = cls.run_animdl_command(cmd)
            return [json.loads(episode.strip()) for episode in result.stdout.strip().split("\n")] # type: ignore
        except:
            return None
    
    @classmethod
    def get_stream_urls_by_anime_title(cls,title:str,episodes_range=None):
        anime = cls.get_anime_url_by_title(title)
        if not anime:
# TODO: raise nostreams exception 
            return None            
        return anime[0],cls.get_stream_urls_by_anime_url(anime[1],episodes_range)
# MOVE ANIMDL DATA PARSERS TO ANOTHER FILE
    @classmethod
    def contains_only_spaces(cls,input_string):
        return all(char.isspace() for char in input_string)

    @classmethod
    def output_parser(cls,result_of_cmd):
        data = result_of_cmd.stderr.split("\n")[3:] # type: ignore
        parsed_data = {}
        pass_next = False
        for i,data_item in enumerate(data[:]):
            if pass_next:
                pass_next = False
                continue
            if not data_item or cls.contains_only_spaces(data_item):
                continue
            item = data_item.split(" / ")
            numbering = r"^\d*\.\s*"
            try:

                anime_title = re.sub(numbering,'',item[0]).lower()
                # special case for onepiece since allanime labels it as 1p instead of onepiece
                one_piece_regex = re.compile(r"1p",re.IGNORECASE)
                if one_piece_regex.match(anime_title):
                    anime_title = "one piece"

                if item[1] == "" or cls.contains_only_spaces(item[1]):
                    pass_next = True
                    parsed_data.update({f"{anime_title}":f"{data[i+1]}"})
                else:                
                    parsed_data.update({f"{anime_title}":f"{item[1]}"})
            except:
                pass
        return parsed_data
# TODO: ADD RUN_MPV_COMMAND = RAISES MPV NOT FOR ND EXCEPTION 
# TODO: ADD STREAM WITH MPV
if __name__ == "__main__":
    # for anime_title,url in AnimdlApi.get_anime_url_by_title("jujutsu").items():
    start = time.time()
    # t = AnimdlApi.get_stream_urls_by_anime_url("https://allanime.to/anime/LYKSutL2PaAjYyXWz")
    title = input("enter title: ")
    e_range = input("enter range: ")
    # t = AnimdlApi.download_anime_by_title(title,lambda *args:print(f"done ep: {args}"),lambda *args:print(f"done {args}"),episodes_range=e_range,quality="worst")
    t=AnimdlApi.stream_anime_by_title(title,e_range)
    # t = os.mkdir("kol")
    # t = run([shutil.which("python"),"--version"])
    # while t.stderr:
    #     print(p,t.stderr)
    # for line in t.stderr:
    
    #     print(line)
    #     print("o")
    delta = time.time() - start
    print(t,shutil.which("python"))
    # print(json.dumps(t[1]))
    print(f"Took: {delta} secs")
    
