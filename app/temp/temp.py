# # import plyer

# # plyer.notification.notify(app_name="Aninforma",message="hello",title="Anime Update")  # type: ignore

# from kivy.properties import StringProperty
# from kivy.uix.widget import Widget
# def get_prop():
#     return StringProperty()

# class app(Widget):
#     def awe(self):
#         self.prop = get_prop

#     def on_prop(self,value,instance):
#         print(
import requests
from inspect import isgenerator
from typing import Generator

def jo():

    if False:
        return {}
    else:
        def _f():
            for i in [1,2,3,4]:
                yield i
        return _f()

# url = "https://upos-bstar1-mirrorakam.akamaized.net/iupxcodeboss/9v/lr/n230705er39jxogp0ap3b823gkkylr9v-1-261210110000.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1715806416&gen=playurlv2&os=akam&oi=2823883151&trid=cdad1de563c743629bdbef3a82d44df0i&mid=1715226141&platform=pc&upsig=02ff8e9f9060bc3437356a7cb6cc1ed1&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&hdnts=exp=1715806416~hmac=836a02ef21ecc1a02034d7d10083bdf97103df2a586d8ba6009d8521abd855ac&bvc=vod&nettype=0&orderid=0,1&logo=00000000&f=i_0_0" 

# url = "https://allanime.pro/apiak/sk.json?sub=dx-ep-LYKSutL2PaAjYyXWz_1_sub_English"

# url = "https://upos-bstar1-mirrorakam.akamaized.net/iupxcodeboss/9v/lr/n230705er39jxogp0ap3b823gkkylr9v-1-2d1301000023.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1715806416&gen=playurlv2&os=akam&oi=2823883151&trid=cdad1de563c743629bdbef3a82d44df0i&mid=1715226141&platform=pc&upsig=419c3e929cd04770d08cb0eb8f95470d&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&hdnts=exp=1715806416~hmac=93ee08fbb96878bc55af2ed52bf9d176d96d93656ff865d59ed817bb04ecdedc&bvc=vod&nettype=0&orderid=0,1&logo=00000000&f=i_0_0"

url = "https://video.wixstatic.com/video/7ef2fd_c718a462da2b43c9b1cae21babfadf2c/480p/mp4/file.mp4"

# r = requests.get(url)


# for cont in r.iter_content(chunk_size=8*1024):
#     print(cont)
from subprocess import run,Popen,PIPE
import re
def download_with_mpv(url,output_path):
    process = Popen(["mpv",url,f"--stream-dump={output_path}"],stderr=PIPE,text=True)
    progress_regex = re.compile(r"\d+/\d+") # eg Dumping 2044776/125359745

    for stream in process.stderr:
        if matches:=progress_regex.findall(stream):
            # current_bytes,total_bytes = [float(val) for val in matches[0].split("/")]
            print(matches)
            # print("percentage download: ",(current_bytes/total_bytes)*100,"%")
            
        else:
            print("hmm")
    

def progress(stream):
    buffer = b""
    for line in iter(lambda: stream.read(),b""):
        # match = progress_regex.search(line)
        # if match:
        # progress = match.group(1)
        buffer += line
    if buffer:
        yield line
        print(f"Progress: {line}%")

# from tqdm import tqdm

# tqdm.

from multiprocessing import Process
import time
pr = Process(target=lambda *_:print("io"),args=(url,"./vid.mp4"))
pr.start()

time.sleep(5)
# print(r.content)
# print(r.headers)
# d = jo()
# h = {}
# print(isgenerator(d))