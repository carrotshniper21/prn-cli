import requests
from bs4 import BeautifulSoup
from pyfzf.pyfzf import FzfPrompt
import subprocess


class MainScraper:
    BASE_URL = "https://www.pornhub.com"

    def __init__(self):
        self.fzf = FzfPrompt()
        self.categories = self.get_url()
        self.videos = self.choose_category()
        self.stored_videos = self.get_videos()

    def get_url(self):
        response = requests.get(f"{self.BASE_URL}/categories")
        soup = BeautifulSoup(response.content, "html.parser")
        elements = soup.find_all(class_="js-mxp")
        categories = []

        for i, element in enumerate(elements):
            url = element.get("href")
            strong_text = element.find("strong")

            if url.startswith("/video?c=") and strong_text is not None:
                categories.append(f"{self.BASE_URL}{url} {strong_text.text}")

        return categories

    def choose_category(self):
        output = self.fzf.prompt(
            self.categories, "--border -1 --reverse --with-nth 2.."
        )
        output_str = "".join(output)
        videos = requests.get(f"{output_str.split()[0]}")

        return videos

    def get_videos(self):
        soup = BeautifulSoup(self.videos.content, "html.parser")
        phimages = soup.find_all("div", class_="phimage")

        stored_videos = []

        for phimage in phimages:
            get_link = phimage.find("a")
            get_title = phimage.find("img")
            link = get_link.get("href")
            title = get_title.get("title")
            stored_videos.append(f"{self.BASE_URL}{link} {title}")

        return stored_videos

    def choose_video(self):
        chosen_video = self.fzf.prompt(
            self.stored_videos, "--border -1 --reverse --with-nth 2.."
        )
        video_watch_url = "".join(chosen_video)
        print("[+] Press Ctrl+C to exit the program")
        result = subprocess.run(
            [
                "mpv",
                f"{video_watch_url.split()[0]}",
                f"--title={video_watch_url.split()[1]}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def main(self):
        self.choose_video()


if __name__ == "__main__":
    scraper = MainScraper()
    scraper.main()
