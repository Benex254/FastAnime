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


# URL of the file you want to download
url = "http://example.com/path/to/file.mp4"

# Options for yt-dlp
ydl_opts = {
    "outtmpl": "/path/to/downloaded/file.%(ext)s",  # Specify the output path and template
    "logger": MyLogger(),  # Custom logger
    "progress_hooks": [my_hook],  # Progress hook
}


# Function to download the file
def download_file(url, options):
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])


# Call the function
download_file(url, ydl_opts)
