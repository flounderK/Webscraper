from Pagescraper import Pagescraper, State
import time


class Bookscraper:
    def __init__(self, session, link, parser_func, downloader_func, book_name="", link_page_number=1):
        """
        Wrapper class for use of Pagescraper, auto increments pages and logs Pagescraper info
        :param session:
        :param link:
        :param parser_func:
        :param downloader_func:
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

        log_file.close()

