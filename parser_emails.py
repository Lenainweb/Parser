#!/usr/bin/python3
"""
Script for searching for e-mail addresses
on the site specified on the command line and
with the required depth of search.

"""
import sys
import re
import requests
import lxml
from bs4 import BeautifulSoup

# Constants
DEFAULT_DEPTH = 0
FORBIDDEN_PREFIXES = ['#', 'tel:']
ADJUSTABLE_PREFIXES = ['http', '//', ' ']

# Lists of all links and emails
ctrl = []
mails =[]

def main():
    """
    Checks the values specified at startup on the command line.
    Starts the parsing function. Displays the received values.

    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Tip: parser_emails.py the_address_where_to_search_for_emails [depth of search]')
        return 1

    url = sys.argv[1]

    if len(sys.argv) is 2:
        depth = DEFAULT_DEPTH
    else:
        depth = int(sys.argv[2])

    mails = add_all_mails_recursive(url, depth)
    if len(mails) == 0:
        print('No emails found.')
    else:
        print ('FOUND E-MAILS:')
        for mail in mails:
            print(mail)
    return 0


def add_all_mails_recursive(url, maxdepth=DEFAULT_DEPTH):
    """
    E-mail search function
    """

    links_to_handle_recursive = []

    # Converts an address to a standard view.
    if not url.startswith('//') and not url.startswith('http'):
        url = 'http://' + url
    if not url.startswith('http'):
        url = 'http:' + url

    domain = url.split('//')[1].split('/')[0]
    # Get the html/
    try:
        request = requests.get(url)

        if request.status_code is not 200:
            return 1
        # Parsing it using BeautifulSoup
        soup = BeautifulSoup(request.content, 'lxml')
        # Consider all tags <a>
        for tag_a in soup.find_all('a'):

            # Get the link corresponding to the tag.
            try:
                link = tag_a['href']

                if all(not link.startswith(f_prefix) for f_prefix in FORBIDDEN_PREFIXES):
                    if all (not link.startswith(a_prefix) for a_prefix in ADJUSTABLE_PREFIXES):
                        link = domain + link

                    if  link.find(domain) != -1  and link not in links_to_handle_recursive and link not in ctrl:
                        links_to_handle_recursive.append(link)
                        ctrl.append(link)
            except:
                continue
            # Using the regular expression, we find emails.
            mail = r"[-a-zA-Z0-9_]{1,100}@[a-z]{1,10}\.[a-z]{2,4}"
            foundaddresses = re.findall(mail, request.text)
            for address in foundaddresses:
                if address and address not in mails:
                    mails.append(address)
    except KeyboardInterrupt:
        exit(1)
    except:
        if maxdepth == int(sys.argv[2]):
            print('This address was not found.')
            exit(1)
        pass

    # If the specified depth of search is not reached, recursively call the function.
    if maxdepth > 0:
        for link in links_to_handle_recursive:
            add_all_mails_recursive(link, maxdepth=maxdepth - 1)

    return  mails


if __name__ == "__main__":
    main()
