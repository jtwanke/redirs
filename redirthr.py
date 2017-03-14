import sys
import os
import requests
import Queue
import threading
import fnmatch
from requests.exceptions import ConnectionError, Timeout


class Test:
    """
    The Test class is responsible for testing and tracing redirections. The constructor takes the name of the file to
    be tested and then prints the results of the test to standard output once the 'start' method has
    been invoked.

    The test class expects a txt or csv file with one or two columns. If the file has two columns, then the first
    column's URL will be issued an HTTP request and the response will be matched against the URL in the second column.
    This produces PASS, FAIL, or CIRCULAR_REDIRECT based on whether the result URL and the second URL match.

    If the file only has one column, then the redirection behavior is traced and returned.
    """
    def __init__(self, input_file):
        self.input_file = input_file
        self.separator = os.path.sep
        self.q = Queue.Queue()
        self.finished = False

    def process_url(self):
        while not self.finished:
            item = self.q.get()
            test_out = Test.test(item[0], item[1])
            sys.stdout.write(test_out)  # Can't use 'print' because it's not thread-safe
            self.q.task_done()

    def start(self):
        """
        This method initiates the redirections test on the input file. Results are sent to standard output.
        :return: Nothing.
        """
        the_test_file = open(self.input_file)
        the_test = the_test_file.readlines()
        if len(the_test) < 1:
            return None
        num_worker_threads = 4
        for i in range(num_worker_threads):
            t = threading.Thread(target=self.process_url)
            t.daemon = True
            t.start()
        for test_case in the_test:
            urls = test_case.split(',')
            url_1 = urls[0].strip()
            if "http" not in url_1:
                url_1 = 'http://' + urls[0].strip()
            if len(urls) > 1 and urls[1].strip():
                url_2 = urls[1].strip()
                if "http" not in url_2:
                    url_2 = 'http://' + urls[0].strip()
                self.q.put((url_1, url_2))
            else:
                self.q.put((url_1, ''))
        self.q.join()  # block until all tasks are done

    @staticmethod
    def test(url_1, url_2=''):
        """ Method used to test re-directions. If url_1 gets redirected to url_2, the test passes.
        Otherwise, it fails. If only one url is passed into the function, then there's no PASS/FAIL,
        only the results of the http trace.

        All http requests and responses are handled using the requests class:
        http://requests.readthedocs.io/en/master/user/quickstart/

        :param url_1: target url to be requested
        :param url_2: the url expected to land on when requesting url_1
        :return: the test results from requesting url_1
        """
        the_test_out = url_1 + ',' + url_2
        is_circular, the_trail = Test.resolve_url(url_1)
        if not the_trail:
            the_test_out += ",FAIL,NO_RESPONSE\n"
            return the_test_out
        if is_circular:
            the_test_out += ",CIRCULAR_REDIRECT "
        elif the_trail[-1][1] == url_2 or the_trail[-1][1] == (url_2 + '/'):
            the_test_out += ",PASS "
        elif url_2:
            the_test_out += ",FAIL "
        else:  # Trace url redirection.
            the_test_out += (the_trail[-1][1] + ",TRACE ")
        if the_trail[-1][0] == 404:
            the_test_out += "(404) "
        if len(the_trail) > 3:
            the_test_out += "(MULT)"
        the_test_out += ","
        the_test_out += Test.print_trail(the_trail)
        the_test_out += "\n"
        return the_test_out

    @staticmethod
    def resolve_url(url):
        try:
            response = requests.get(url, timeout=10, allow_redirects=False)
        except ConnectionError or Timeout:
            return False, []
        return Test.resolve_response(response, [('', url)])

    @staticmethod
    def resolve_response(response, trail):
        """
        Recursively resolves the http response until a circular redirection is detected or a final response code is
        issued (any response that isn't 301 or 302 will be considered final).
        :param response: http response ()
        :param trail: an array of tuples representing the trail of redirections
        :return: bool circular_redirect, list of (status, url) tuples
        """
        if response.is_redirect:
            status = response.status_code
            if response.headers:
                loc = response.headers['location']
                is_circular = Test.audit_trail(trail, loc)
                trail.append((status, loc))
                if is_circular:
                    return True, trail
                try:
                    new_response = requests.get(loc, allow_redirects=False, timeout=10)
                    return Test.resolve_response(new_response, trail)
                except ConnectionError or Timeout:
                    return False, trail
        else:
            trail.append((response.status_code, response.url))
            return False, trail

    @staticmethod
    def audit_trail(trail, url):
        """
        Audits the trail for the given url. If the url is present, it returns True. Otherwise, it returns False.
        :param trail: an array of tuples representing the trail
        :param url: the url we are looking for
        :return:
        """
        for destination in trail:
            if destination[1] == url:
                return True
        return False

    @staticmethod
    def print_trail(trail):
        """
        Prints the trail of http redirections.
        :param trail:
        :return:
        """
        out_string = ''
        for item in trail:
            if str(item[0]).strip():
                out_string += ("(" + str(item[0]) + ") " + item[1] + " ==> ")
            elif item[1].strip():
                out_string += (item[1] + " ==> ")
            else:
                out_string += ("invalid_item" + " ==> ")
        return out_string[:len(out_string) - 4]


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print "Usage Examples:"
        print "python redirthr.py redirections.csv"
        print "python redirthr.py redirections.txt"
        print "python redirthr.py dir"
        sys.exit()
    inputFile = sys.argv[1]  # file (i.e. urls.csv)
    if os.path.isdir(inputFile):  # batch
        for root, dirnames, filenames in os.walk(inputFile):
            for filename in fnmatch.filter(filenames, '*.csv'):
                thetest = Test(os.path.join(root, filename))
                thetest.start()
        for root, dirnames, filenames in os.walk(inputFile):
            for filename in fnmatch.filter(filenames, '*.txt'):
                thetest = Test(os.path.join(root, filename))
                thetest.start()
    else:
        thetest = Test(inputFile)
        thetest.start()
