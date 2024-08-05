import yt_dlp


class MyLogger:
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d["status"] == "finished":
        print("Done downloading, now converting ...")


# URL of the HLS stream
url = "https://example.com/path/to/stream.m3u8"

# Options for yt-dlp
ydl_opts = {
    "format": "best",  # Choose the best quality available
    "outtmpl": "/path/to/downloaded/video.%(ext)s",  # Specify the output path and template
    "logger": MyLogger(),  # Custom logger
    "progress_hooks": [my_hook],  # Progress hook
}


# Function to download the HLS video
def download_hls_video(url, options):
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])


# Call the function
download_hls_video(url, ydl_opts)
