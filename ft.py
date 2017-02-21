from html.parser import HTMLParser
import requests
import sys

def attr_is_class(attr):
    return attr[0] == 'class'

def is_num(elem):
    return elem.isnumeric()

def is_most_read(elem):
    if elem.lower() == 'most_read' or elem.lower() == 'most read' or elem.lower() == 'most.read' or elem.lower() == 'mostread':
        return True

def finder(test, list):
    for l in list:
        if test(l):
            return l

class FtParser(HTMLParser):
    collection = []
    capture_next = False
    start_after = -1

    def __init__(self, class_to_find, start_after_this_class, mr):
        super().__init__()
        self.class_to_find = class_to_find
        self.start_after_this_class = start_after_this_class
        self.mr = mr

    def handle_starttag(self, tag, attrs):
        class_attr = finder(attr_is_class, attrs)
        if class_attr and self.start_after_this_class in class_attr[1]:
            self.start_after = 0
        elif class_attr and self.class_to_find in class_attr[1]:
            self.capture_next = True

    def handle_data(self, data):
        content = data.strip()
        if (not self.mr) and content and (self.start_after < 0 or self.start_after >= 5)  and self.capture_next:
            self.collection.append(content)
        elif content and (self.start_after >= 0 and self.start_after < 5)  and self.capture_next:
            if self.mr:
                self.collection.append(content)
            self.start_after = self.start_after + 1
        self.capture_next = False

def printer(limit, most_read):
    if most_read:
        parser = FtParser('js-teaser-heading-link', 'o-teaser-collection__heading o-teaser-collection__heading--full-width', True)
        limit = 5
    else:
        parser = FtParser('js-teaser-heading-link', 'o-teaser-collection__heading o-teaser-collection__heading--full-width', False)
    req = requests.get('https://www.ft.com')
    parser.feed(req.text)
    titles = parser.collection[0:limit]
    for title in titles:
        print('->', title)

def main():
    limit = finder(is_num, sys.argv)
    if not limit:
        limit = 20
    most_read = False
    if finder(is_most_read, sys.argv):
        most_read = True
    printer(int(limit), most_read)

main()
