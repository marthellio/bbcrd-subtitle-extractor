import requests
import argparse
import xml.etree.ElementTree as ET


def get_episode_data(episode_pid):
    api_for_episode_versions = "https://api.live.bbc.co.uk/pips/api/v1/episode/pid." + episode_pid + "/versions/"
    print("url = "+ api_for_episode_versions)
    response = requests.get(api_for_episode_versions)
    print("Status = "+response.status_code)
    print("Content = "+response.content)

def parseOptions():
        parser = argparse.ArgumentParser(description='InputOptions')
        parser.add_argument('pid', type=str, nargs='+')
        opts = parser.parse_args()
        return opts

args = parseOptions()
print(args.pid)
get_episode_data(args.pid[0])