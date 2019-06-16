from enum import Enum
import os


class State(Enum):
    STARTING = 0
    READY_FOR_SESSION = 1
    RUNNING_DOWNLOADER = 2
    RUNNING_PARSER = 3
    PARSER_ERROR = 4
    DOWNLOADER_ERROR = 5
    FINISHED = 6
    ERROR = 7


class Pagescraper:
    def __init__(self, link, page_number, parser_func, downloader_func, retry_count=3, downloader_path=os.getcwd()):
        """
        Template for a scraper designed to download a page, find a specific link in the page, and
        download other specified files from the page. The user must supply a function for downloading and parsing.
        Parsing in this context is only meant to locate the next link and download all of the relevant files for this
        page.
        :param link:
        :param page_number:
        :param parser_func:
        :param downloader_func:
        :param retry_count:
        :param downloader_path:
        """
        self.state = State.READY_FOR_SESSION
        self.page_link = link
        self.next_link = ""
        self.additional_links = dict()
        self.parser_func = parser_func
        self.downloader_func = downloader_func
        self.retry_count = retry_count
        self.retrys = retry_count
        self.page_number = page_number
        self.downloaded_files = list()
        self.session = None
        self.downloader_path = downloader_path
        self.file_name = os.path.join(self.downloader_path, f"page{page_number}.html")
        self.log_file_name = os.path.join(self.downloader_path, f"page{page_number}.log")
        self.first_downloader_pass = True
        self.additional_link_generator = None

    def downloader(self, link, file_name):
        """Downloader function should take in a session, a link, and the name of the file to create.
        Nothing should be returned, but exceptions may be raised"""
        try:
            self.downloader_func(self.session, link, file_name)
        except Exception as err:
            self.state = State.DOWNLOADER_ERROR
            self.retry_count -= 1
        self.first_downloader_pass = False

    def parser(self, file):
        """parser should accept a file name parameter and return a tuple in the form:
        (next_link, {additional_link: filename, additional_link: filename})"""
        try:
            self.next_link, self.additional_links = self.parser_func(file)
            self.additional_link_generator = self.__get_additional_link()
            self.state = State.RUNNING_DOWNLOADER
        except Exception as err:
            self.state = State.PARSER_ERROR

    def give_session(self, session):
        """Allow this instance to take control of the session"""
        self.session = session
        self.state = State.RUNNING_DOWNLOADER
        self.runner()

    def take_session(self):
        """take control of the session and remove it from this instance"""
        session = self.session
        self.session = None
        return session

    def __get_additional_link(self):
        for key in self.additional_links.keys():
            yield key
        yield None

    def runner(self):
        while True:
            if self.state == State.READY_FOR_SESSION:
                if self.session is not None:
                    pass
            elif self.state == State.RUNNING_DOWNLOADER:
                if self.first_downloader_pass is True:
                    self.downloader(self.page_link, self.file_name)
                    self.downloaded_files.append(self.file_name)
                    self.state = State.RUNNING_PARSER
                else:
                    link = next(self.additional_link_generator)
                    if link is None:
                        self.state = State.FINISHED
                        continue
                    for retry in range(0, self.retrys):
                        try:
                            new_file_path = os.path.join(self.downloader_path, self.additional_links[link])
                            self.downloader(link, new_file_path)
                            self.downloaded_files.append(new_file_path)
                            break
                        except Exception as err:
                            pass

            elif self.state == State.RUNNING_PARSER:
                self.parser(self.file_name)
            elif self.state == State.DOWNLOADER_ERROR:
                if self.retry_count == 0:
                    self.state = State.ERROR
                else:
                    self.state = State.RUNNING_DOWNLOADER
            elif self.state == State.FINISHED:
                break
            elif self.state == State.PARSER_ERROR or self.state == State.ERROR:
                break

    def __repr__(self):
        return f"State: {self.state}\n" \
                f"Page link: {self.page_link}\n"\
                f"Next page link: {self.next_link}\n"\
                f"downloaded files: {', '.join([i for i in self.downloaded_files])}\n"\
                f"additional links: {self.additional_links}\n"


