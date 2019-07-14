from AbsPagescraper import AbsPagescraper, State, ParserReturn
from Bookscraper import Bookscraper
import unittest


class TestPagescraper(AbsPagescraper):

    def parser(self, filename):
        """Fake parser"""
        additional_link_dict = {"http://fakeadditionallink/stuff.css": "stuff.css",
                                "http://anotherfakeadditionallink/stuff.jpg": "stuff.jpg"}
        return ParserReturn("http://fakenextlink.html", additional_link_dict)

    def downloader(self, session, link, filename):
        pass


class PagescraperTest(unittest.TestCase):
    def setUp(self):
        self.page_scraper = TestPagescraper("originallink", 1)

    def testpagescraper(self):

        self.page_scraper.give_session("session")
        self.assertEqual(self.page_scraper.state, State.FINISHED)

    def testbookscraper(self):
        book_scraper = Bookscraper("session", "link", self.page_scraper.__class__, book_name="bookname",
                                   max_page_count=25)
        try:
            book_scraper.run()
        except Exception as err:
            self.fail("Error hit while running book scraper")


if __name__ == '__main__':
    unittest.main()
