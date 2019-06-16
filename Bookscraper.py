from Pagescraper import Pagescraper, State
import time
import requests
import shutil
import os
# TODO: Find a good way to mark the end of a book


class Bookscraper:
    def __init__(self, session, link, parser_func, downloader_func, book_name, end_link=None, max_page_count=None,
                 link_page_number=1):
        """
        Wrapper class for use of Pagescraper, auto increments pages and logs Pagescraper info
        :param session:
        :param link:
        :param parser_func:
        :param downloader_func:
        :param book_name:
        :param end_link:
        :param max_page_count:
        :param link_page_number:
        """
        self.start_link = link
        self.start_link_page_number = link_page_number
        self.current_link = link
        self.current_page_number = link_page_number
        self.session = session
        self.parser_func = parser_func
        self.downloader_func = downloader_func
        self.book_name = book_name
        self.output_path = os.path.join(os.getcwd(), self.book_name)
        self.log_file = os.path.join(self.output_path, f"Bookscraper_{self.book_name}.log")
        self.end_link = end_link
        self.max_page_count = max_page_count
        self.current_page_count = 0
        os.makedirs(self.output_path, exist_ok=True)

        if self.end_link is None and self.max_page_count is None:
            print("Running a bookscraper without setting an end_link or max_page_count will likely end in "
                  "a parsing error or the book scraper beginning to download the whole book again (debpending on "
                  "the configuration of the targeted website. Also doing that could fill up your drive, so don't)")

    def run(self):
        log_file = open(self.log_file, "w")
        while True:
            downloader_path = os.path.join(self.output_path, f"{self.current_page_number}")
            os.makedirs(downloader_path, exist_ok=True)
            page_scraper = Pagescraper(self.current_link, self.current_page_number,
                                       self.parser_func, self.downloader_func, downloader_path=self.output_path)
            page_scraper.give_session(self.session)
            while page_scraper.state != State.FINISHED and page_scraper.state != State.PARSER_ERROR and \
                    page_scraper.state != State.ERROR:
                time.sleep(0.5)

            if page_scraper.state == State.ERROR or page_scraper.state == State.PARSER_ERROR:
                log_file.write(f"""Page scraper failure on page {self.current_page_number}
                                Page info: 
                                {page_scraper}\n""")
                print("Page scraping error")
                break

            if page_scraper.state == State.FINISHED:
                log_file.write(f"{page_scraper}\n\n")
                self.current_link = page_scraper.next_link
                self.current_page_number += 1
                self.session = page_scraper.take_session()

            if self.current_page_count is not None:
                self.current_page_number += 1

            if self.current_page_count == self.max_page_count or self.current_link == self.end_link:
                break

        log_file.close()


def downloader(session: requests.session, url: str, filename: str, **kwargs):
    with session.get(url, stream=True, **kwargs) as r:
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        else:
            raise Exception("Failed to connect")





