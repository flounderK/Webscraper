from Pagescraper import Pagescraper, State
import time

# TODO: Find a good way to mark the end of a book


class Bookscraper:
    def __init__(self, session, link, parser_func, downloader_func, end_link=None, max_page_count=None,
                 book_name="", link_page_number=1):
        """
        Wrapper class for use of Pagescraper, auto increments pages and logs Pagescraper info
        :param session:
        :param link:
        :param parser_func:
        :param downloader_func:
        :param end_link:
        :param max_page_count:
        :param book_name:
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
        self.log_file = f"Bookscraper_{self.book_name}.log"
        self.end_link = end_link
        self.max_page_count = max_page_count
        self.current_page_count = 0

        if self.end_link is None and self.max_page_count is None:
            print("Running a bookscraper without setting an end_link or max_page_count will likely end in "
                  "a parsing error or the book scraper beginning to download the whole book again (debpending on "
                  "the configuration of the targeted website)")

    def run(self):
        log_file = open(self.log_file, "w")
        while True:
            page_scraper = Pagescraper(self.current_link, self.current_page_number,
                                       self.parser_func, self.downloader_func)
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

