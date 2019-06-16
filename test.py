from Pagescraper import Pagescraper, State
from Bookscraper import Bookscraper
import unittest


def mock_parser(file_name):
    return "http://fakenextlink.html", {"http://fakeadditionallink/stuff.css": "stuff.css",
                                        "http://anotherfakeadditionallink/stuff.jpg": "stuff.jpg"}


def mock_downloader(session, link, file_name):
    pass


class PagescraperTest(unittest.TestCase):
    def testpagescraper(self):
        page_scraper = Pagescraper("originallink", 1, mock_parser, mock_downloader)
        page_scraper.give_session("session")
        self.assertEqual(page_scraper.state, State.FINISHED)

    def testbookscraper(self):
        book_scraper = Bookscraper("session", "link", mock_parser, mock_downloader, book_name="bookname",
                                   max_page_count=25)
        try:
            book_scraper.run()
        except Exception as err:
            self.fail("Error hit while running book scraper")


if __name__ == '__main__':
    unittest.main()
