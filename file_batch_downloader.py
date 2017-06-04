import os
from bs4 import BeautifulSoup

def file_batch_downloader(url, suffix):
    """Download all files with specific type on a website.
    """
    html = os.popen('curl ' + url)  # Get HTML content.
    current_dir = os.path.dirname(url) + '/'

    # Extract file URLs to a list.
    soup = BeautifulSoup(html, 'html5lib')
    file_url_list = []
    for a in soup.find_all('a'):
        file_url = str(a.get('href'))
        if file_url.endswith(suffix):
            file_url = current_dir + file_url
            file_url_list.append(file_url)

    # Download files.
    for file_url in file_url_list:
        os.system('wget ' + file_url)

def main():
    file_batch_downloader('http://15415.courses.cs.cmu.edu/fall2016/syllabus.html', 'pdf')

if __name__ == '__main__':
    main()