from subprocess import run, PIPE
from difflib import SequenceMatcher
import time
import json
import re



class AnimdlApi:
    @classmethod
    def run_command(cls,cmds:list):
        return run(["C:\\Users\\bxavi\\.pyenv\\pyenv-win\\versions\\3.10.11\\python.exe","-m", "animdl", *cmds],capture_output=True,stdin=PIPE,text=True)

    @classmethod
    def get_anime_match(cls,anime_item,title):
        return SequenceMatcher(None,title,anime_item[0]).ratio()
    
    @classmethod
    def get_anime_url_by_title(cls,title:str):
        result = cls.run_command(["search",title])
        possible_animes = cls.output_parser(result)
        if possible_animes:
            anime_url = max(possible_animes.items(),key=lambda anime_item:cls.get_anime_match(anime_item,title))
            return anime_url # {"title","anime url"}
        return None
    
    @classmethod
    def get_stream_urls_by_anime_url(cls,anime_url:str):
        if anime_url:
            try:
                result = cls.run_command(["grab",anime_url])
                return [json.loads(episode.strip()) for episode in result.stdout.strip().split("\n")]
            except:
                return None
        return None
    
    @classmethod
    def get_stream_urls_by_anime_title(cls,title:str):
        anime = cls.get_anime_url_by_title(title)
        if anime:
            return anime[0],cls.get_stream_urls_by_anime_url(anime[1])
        return None            


    @classmethod
    def contains_only_spaces(cls,input_string):
        return all(char.isspace() for char in input_string)

    @classmethod
    def output_parser(cls,result_of_cmd:str):
        data = result_of_cmd.stderr.split("\n")[3:]
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
                if item[1] == "" or cls.contains_only_spaces(item[1]):
                    pass_next = True
                    
                    parsed_data.update({f"{re.sub(numbering,'',item[0])}":f"{data[i+1]}"})
                else:                
                    parsed_data.update({f"{re.sub(numbering,'',item[0])}":f"{item[1]}"})
            except:
                pass
        return parsed_data


if __name__ == "__main__":
    # for anime_title,url in AnimdlApi.get_anime_url_by_title("jujutsu").items():
    # t = AnimdlApi.get_stream_urls_by_anime_url("https://allanime.to/anime/LYKSutL2PaAjYyXWz")
    start = time.time()
    t = AnimdlApi.get_stream_urls_by_anime_title("KONOSUBA -God's Blessing on This Wonderful World! 3")
    delta = time.time() - start
    print(t)
    print(f"Took: {delta} secs")
    
