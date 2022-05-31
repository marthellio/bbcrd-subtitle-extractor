import requests
import argparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re
import os
import pandas
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
username = os.path.expanduser('~')
certificate_path = username + "/.ssh/dev.bbc.co.uk.pem"

def read_input():
    args = parseOptions()
    if args.file:
        df = pandas.read_csv(args.file)
        subtitles = []
        print("PIDs to look up:")
        print(df['episode'])
        for pid in df['episode']:
            text = get_subtitle_text_from_pid(pid)
            subtitles.append(text)
        df['subtitles'] = subtitles
        print(" - Writing to JSON")
        df.to_json(path_or_buf='/home/marthellio/GitRepos/bbcrd-subtitle-extractor/output.jsonl', orient='records', lines=True)

    elif args.pid:
        text = get_subtitle_text_from_pid(args.pid)
        print(text[0:50])

def parseOptions():
        parser = argparse.ArgumentParser(description='InputOptions')
        #parser.add_argument('pid', type=str, nargs='+')
        parser.add_argument('-p','--pid', type=str, help="The input pid.")
        parser.add_argument('-f','--file', type=str, help="The input file(s) containing pids in column A.")
        opts = parser.parse_args()
        return opts

def get_subtitle_text_from_pid(pid):
    subtitle_url = get_subtitle_url_from_pid(pid)
    if subtitle_url == "Error":
        return "Error"
    else:
        subtitle_text = str(get_subtitle_text_from_url(subtitle_url))
    return subtitle_text

def extract_data_from_url(url):
    print(" - Looking up URL: "+ str(url))
    response = requests.get(
        url,
        cert=certificate_path,
        verify=False
    )
    return response.content

def get_subtitle_url_from_pid(episode_pid):
    print("***************************\n Looking up PID: " + str(episode_pid))
    episode_versions_url = "https://api.live.bbc.co.uk/pips/api/v1/episode/pid." + episode_pid + "/versions/"
    episode_versions_data = extract_data_from_url(episode_versions_url)

    episode_versions_soup = BeautifulSoup(episode_versions_data)
    versions = []
    for version in episode_versions_soup.find_all('version', href=True):
        versions.append(version['href'])

    first_version_url=versions[0]
    media_assets_url = first_version_url+ "media_assets/"

    subtitle_available = None
    files = []
    page_no = 1

    while ((subtitle_available == None) and (page_no<=10)):
        media_assets_page_url = media_assets_url + "?page="+ str(page_no)
        media_assets_page_data = extract_data_from_url(media_assets_page_url)
        media_assets_page_soup = BeautifulSoup(media_assets_page_data)
        filename_list = media_assets_page_soup.find_all('filename')

        for line in filename_list:
            filename = line.get_text()
            files.append(filename)

        for file in files:
            subtitle_available = re.search('^ng/modav/', file)

        page_no += 1

    if subtitle_available != None:
        subtitles_files = [i for i in files if i.startswith('ng/modav/')]
        subtitle_file_url = "https://livemodavsharedresources-publicstaticbucket-16n1nhlyoptzf.s3.amazonaws.com/iplayer/subtitles/" + subtitles_files[0]
        print(" - Subtitles located at "+ subtitle_file_url)
        return subtitle_file_url
    else:
        print(" - Subtitles could not be located.")
        return "Error"

def get_subtitle_text_from_url(url):
    subtitle_file_data = extract_data_from_url(url)
    html = BeautifulSoup(subtitle_file_data, 'lxml')
    entries = html.find_all('span')
    text = ""

    for entry in entries:
        line = entry.get_text()
        line = process_line(line)

        if line is not None:
            text += line + " "
    #print("Subtitles = "+ text)
    return text

def process_line(line):
    line = re.sub('[\n\r]+', ' ', line)
    line = line.strip()

    if len(line) == 0:
        return None

    return line

read_input()
