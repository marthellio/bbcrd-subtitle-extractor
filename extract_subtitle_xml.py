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
working_directory = os.getcwd()

def read_input():
    args = parseOptions()
    if args.file:
        print("Reading from file: " + args.file)
        df = pandas.read_csv(args.file)
        print(" - PIDs to look up:")
        print(df['episode'])

        subtitles = []
        for pid in df['episode']:
            text = get_subtitle_text_from_pid(pid)
            subtitles.append(text)
            print(" - Completed search.")
        df['subtitles'] = subtitles

        if args.output:
            output_file_path = working_directory + "/" + args.output
        else:
            output_file_path = working_directory + "/output.jsonl"
        print(" - Writing to JSON: " + output_file_path)
        df.to_json(path_or_buf=output_file_path, orient='records', lines=True)

    elif args.pid:
        text = get_subtitle_text_from_pid(args.pid)
        print(text[0:50])

    else:
        print("No episode PIDs supplied. Please append '--pid <enter PID here>' or '--file <enter file containing PIDs here>'.")

def parseOptions():
        parser = argparse.ArgumentParser(description='InputOptions')
        #parser.add_argument('pid', type=str, nargs='+')
        parser.add_argument('-p','--pid', type=str, help="The input pid.")
        parser.add_argument('-f','--file', type=str, help="The input file containing pids in column A.")
        parser.add_argument('-o','--output', type=str, help="The output file name. This will be saved to the current working directory. Default is 'output.jsonl'.")
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
    print("\n***************************************************************\n Looking up PID: " + str(episode_pid))
    episode_versions_url = "https://api.live.bbc.co.uk/pips/api/v1/episode/pid." + episode_pid + "/versions/"
    episode_versions_data = extract_data_from_url(episode_versions_url)

    first_version_url = get_first_version_url_from_episode_version_data(episode_versions_data)
    media_assets_url = first_version_url+ "media_assets/"

    subtitle_file = ""
    page_no = 1

    while ((subtitle_file == "") and (page_no<=10)):
        media_assets_page_url = media_assets_url + "?page="+ str(page_no)
        media_assets_page_data = extract_data_from_url(media_assets_page_url)
        media_assets_page_soup = BeautifulSoup(media_assets_page_data, 'lxml')
        filename_list = media_assets_page_soup.find_all('filename')

        for line in filename_list:
            file = line.get_text()
            if file.startswith('ng/modav'):
                subtitle_file = file
                break

        page_no += 1

    if (subtitle_file != ""):
        subtitle_file_url = "https://livemodavsharedresources-publicstaticbucket-16n1nhlyoptzf.s3.amazonaws.com/iplayer/subtitles/" + subtitle_file
        print(" - Subtitles located at "+ subtitle_file_url)
        return subtitle_file_url
    else:
        print(" - Subtitles could not be located.")
        return "Error"

def get_first_version_url_from_episode_version_data(episode_versions_data):
    episode_versions_soup = BeautifulSoup(episode_versions_data, 'lxml')
    versions = []
    for version in episode_versions_soup.find_all('version', href=True):
        versions.append(version['href'])
    return versions[0]


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
