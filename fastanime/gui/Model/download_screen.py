from .base_model import BaseScreenModel


class DownloadsScreenModel(BaseScreenModel):
    """
    Handles the download screen logic
    """

    def update_download_progress(self, d):
        print(
            d["filename"],
            d["downloaded_bytes"],
            d["total_bytes"],
            d.get("total_bytes"),
            d["elapsed"],
            d["eta"],
            d["speed"],
            d.get("percent"),
        )
        if d["status"] == "finished":
            print("Done downloading, now converting ...")


__all__ = ["DownloadsScreenModel"]
