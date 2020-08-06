import sys


def cli():
    """Defines a simple commandline interface"""
    try:
        search = sys.argv[1]
        pages = sys.argv[2]
    except IndexError:
        print("Usage: scraper <search-term> <pages>")
    try:
        pages = int(pages)
    except:
        print("Second parameter must be an integer (number of pages to be checked)")
        sys.exit()

    return search, pages
