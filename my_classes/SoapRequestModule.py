import httplib
import xml.etree.ElementTree as ET


class SoapRequestSender(object):
    def __init__(self, formula=None, identifiers=None, output=''):
        self.formula = formula
        self.identifiers = identifiers
        self.output = output
        self.uuid = None
        self.product_id = None
        self.template = None
        self.headers = None
        self.url = None
        self.method = None
        self.address = None
        self.soap_message = None
        self.request = None

    def set_uuid(self, value):
        self.uuid = value
        return self

    def set_product_id(self, value):
        self.product_id = value
        return self

    def set_url(self, value):
        self.url = value
        return self

    def set_method(self, value):
        self.method = value
        return self

    def set_address(self, value):
        self.address = value
        return self

    def set_template(self, value):
        self.template = value
        return self

    def set_headers(self, value):
        self.headers = value
        return self

    def __add_headers(self):
        self.request = httplib.HTTP(self.url)
        self.request.putrequest(self.method, self.address)
        for key, value in self.headers.items():
            self.request.putheader(key, value)
        self.request.putheader("Content-length", "%d" % len(self.soap_message))
        self.request.endheaders()

    def update(self, formula, identifiers, output):
        self.formula = formula
        self.identifiers = identifiers
        self.output = output
        self.soap_message = self.template % (self.uuid,
                                             self.product_id,
                                             self.formula,
                                             self.identifiers,
                                             self.output)
        return self

    def send_request(self):
        self.update(self.formula, self.identifiers, self.output)
        self.__add_headers()
        self.request.send(self.soap_message)
        status_code, status_message, status_header = \
            self.request.getreply()
        output_data = self.request.getfile()\
            .read(int(status_header['Content-length']))
        self.request.close()
        return Result(status_code, status_message,
                      status_header, output_data)


class Result(object):
    def __init__(self, status_code,
                 status_message,
                 status_header,
                 input_data):
        self.status_code = status_code
        self.status_message = status_message
        self.status_header = status_header
        self.input_data = input_data
        self.output_dict = {}

    def parse_results(self):
        if self.input_data:
            root = ET.fromstring(self.input_data)
            body = root[1][0]
            rows, columns = int(body.attrib['rows']), int(body.attrib['cols'])
            current_key = "None"
            tag_counter = 0
            for row in body:
                for tag in row:
                    tag_counter += 1
                    if (tag_counter % columns) == 1 and tag_counter > columns:
                        current_key = tag.text
                        if current_key not in self.output_dict.keys():
                            self.output_dict[current_key] = []
                        else:
                            continue
                    elif (columns - (tag_counter % columns)) == columns \
                            and tag_counter > columns:
                        if tag.get('f') == "0" and not tag.text:
                            self.output_dict[current_key].append(None)
                        elif tag.get('t') == 'n':
                            self.output_dict[current_key].append(None)
                        elif tag.get('t') == 'f':
                            if tag.text == 'NaN':
                                self.output_dict[current_key].append('NaN')
                            else:
                                value = float(tag.text)
                                self.output_dict[current_key].append(value)
                        elif tag.get('t') == 'i':
                            value = int(tag.text)
                            self.output_dict[current_key].append(value)
                        elif tag.get('t') == 'b':
                            if tag.text in ('1', 'True'):
                                self.output_dict[current_key].append(True)
                            elif tag.text in ('0', 'False'):
                                self.output_dict[current_key].append(False)
                            else:
                                self.output_dict[current_key].append(None)
        return self.output_dict
