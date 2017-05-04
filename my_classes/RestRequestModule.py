import urllib
import urllib2
import json


class RestRequestSender(object):
    def __init__(self, formula=None, identifiers=None, output=None):
        self.formula = formula
        self.identifiers = identifiers
        self.output = output
        self.product_id = None
        self.headers = None
        self.url = None
        self.rest_message = None
        self.request = None
        self.response = None

    def set_product_id(self, value):
        self.product_id = value
        return self

    def set_url(self, value):
        self.url = value
        return self

    def set_headers(self, value):
        self.headers = value
        return self

    def __encode_values(self):
        self.rest_message = urllib.urlencode({'formula': self.formula,
                                              'identifiers': self.identifiers,
                                              'productid': self.product_id,
                                              'output': self.output})

    def __add_headers(self):
        for key, value in self.headers.items():
            self.request.add_header(key, value)
        self.request.add_header('Content-length', "%d" % len(self.rest_message))
        return self

    def send_request(self):
        self.__encode_values()
        self.request = urllib2.Request(self.url, self.rest_message)
        self.__add_headers()
        self.response = urllib2.urlopen(self.request)
        return Result(self.response)


class Result(object):
    def __init__(self, response_data):
        self.response_data = response_data
        self.parsed_output = {}

    def parse_results(self):
        if self.response_data:
            json_data = json.load(self.response_data)
            for column in json_data['rows'][1::]:
                if column[0] in self.parsed_output.keys():
                    self.parsed_output[column[0]].append(column[-1])
                else:
                    self.parsed_output[column[0]] = [column[-1]]
        return self.parsed_output
