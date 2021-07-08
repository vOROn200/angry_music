import logging
import os
from bs4 import BeautifulSoup
from sendgrid.helpers.mail import *
import requests
import redis
import sendgrid
from jinja2 import Template


def get_albums(link):
    logging.info('parsing link: {}'.format(link))
    r = requests.get(link)
    html_doc = r.content.decode('utf-8', 'ignore')
    soup = BeautifulSoup(html_doc, 'html.parser')
    albums = []
    for article in soup.find_all('article'):
        album = article.find('h2', 'entry-title').find('a')
        link_album = album.get('href')
        title_album = album.get_text().replace('Review', '').strip()
        result = {'link': link_album, 'title': title_album}
        logging.debug(result)
        albums.append(result)
    return albums


def check_new_album(albums):
    r = redis.Redis(host='redis', port=6379, db=0)
    new_albums = []
    for album in albums:
        if r.get(album["link"]) is None:
            logging.info("New: {}".format(album["title"]))
            new_albums.append(album)
            r.set(album["link"], album["title"])
    return new_albums


def send_to_mail(content_body):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ['SENDGRID_TOKEN'])
    from_email = Email("angry_music@hyperlab.work")
    to_email = To("artem.yushkov@gmail.com")
    subject = "New best albums"
    content = Content("text/html", content_body)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    logging.info("Send Mail : status code = {}".format(response.status_code))


def get_content(albums, count_links):
    html = open('email.html').read()
    template = Template(html)
    return template.render(albums_list=albums, count_links=count_links)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    links = [
        'https://www.angrymetalguy.com/tag/50/', 'https://www.angrymetalguy.com/tag/45/', 'https://www.angrymetalguy.com/tag/40/'
    ]
    for count_links, link in enumerate(links):
        albums = get_albums(link)
        new_albums = check_new_album(albums)
        if len(new_albums) > 0:
            content_body = get_content(new_albums, count_links)
            send_to_mail(content_body)
