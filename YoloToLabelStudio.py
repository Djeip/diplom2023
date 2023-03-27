import argparse
import datetime
import glob
import hashlib
import json
import os
import random
import requests
import string
import sys

from PIL import Image
from requests.auth import HTTPBasicAuth


def gen_ascii_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(length))


def gen_labelstudio_json(data, repo, commit, user_info):
    labelstudio = os.path.join(repo, '.labelstudio')
    os.makedirs(labelstudio, exist_ok=True)

    results = []

    # try:
    #     img = Image.open(os.path.join(repo, data))
    # except:
    #     print(f"WARNING: Invalid image '{data}'")
    #     return
    img = Image.open(os.path.join(repo, data))

    label = data.replace("images", "labels")
    label = os.path.splitext(label)[0] + '.txt'
    label_fullpath = os.path.join(repo, label)

    if not os.path.exists(label_fullpath):
        return

    with open(label_fullpath) as f:
        lines = f.read().split('\n')[:-1]

    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'

    for line in lines:
        _, cx, cy, w, h = [float(p) for p in line.split()]
        result = {}
        result["id"] = gen_ascii_string(10)
        result["type"] = "rectanglelabels"
        result["value"] = {}
        result["value"]["x"] = 100.0 * (cx - (w / 2))
        result["value"]["y"] = 100.0 * (cy - (h / 2))
        result["value"]["width"] = 100.0 * w
        result["value"]["height"] = 100.0 * h
        result["value"]["rotation"] = 0
        result["value"]["rectanglelabels"] = ["squirrel"]
        result["origin"] = "manual"
        result["to_name"] = "image"
        result["from_name"] = "label"
        result["image_rotation"] = 0
        result["original_width"] = img.size[0]
        result["original_height"] = img.size[1]
        results.append(result)

    name = user_info.get('full_name', '').split()
    if len(name) > 1:
        first_name = name[0]
        last_name = name[-1]
    elif len(name) > 0:
        first_name = name[0]
        last_name = ''
    else:
        first_name = ''
        last_name = ''

    annotation = {}
    annotation['completed_by'] = {}
    annotation['completed_by']['username'] = user_info.get('username', '')
    annotation['completed_by']['first_name'] = first_name
    annotation['completed_by']['last_name'] = last_name
    annotation['completed_by']['avatar'] = user_info.get('avatar_url', '')
    annotation['result'] = results
    annotation['was_cancelled'] = False
    annotation['ground_truth'] = False
    annotation['created_at'] = timestamp
    annotation['updated_at'] = timestamp
    annotation['lead_time'] = 42.0
    annotation['prediction'] = {}
    annotation['parent_prediction'] = None
    annotation['parent_annotation'] = None

    ls_json = {}
    ls_json['annotations'] = [annotation]
    ls_json['drafts'] = []
    ls_json['predictions'] = []
    ls_json['data'] = {}
    ls_json['data']['image'] = f'repo://{commit}/{data}'
    ls_json['meta'] = {}

    json_file = hashlib.sha1(data.encode("utf-8")).hexdigest() + '.json'
    json_file = os.path.join(labelstudio, json_file)

    with open(json_file, mode='w') as f:
        json.dump(ls_json, f)


def is_image(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in ('.jpg', '.jpeg', '.png')


def get_user_info(user, token):
    url = f'https://dagshub.com/api/v1/users/{user}'
    auth = HTTPBasicAuth(user, token)
    res = requests.get(url, auth=auth)

    try:
        info = json.loads(res.content)
        return info
    except:
        print(f'WARNING: Invalid JSON received from server when looking up {user}')
        print(res.content)
        return {}


def main():
    parser = argparse.ArgumentParser(
        'Create LabelStudio compatible annoations from a YOLO-style dataset, within a repo')
    parser.add_argument('--repo', required=True, help='Path to the repo')
    parser.add_argument('--data', required=True, help='Path to folder or single image within the repo to convert')
    parser.add_argument('--commit', required=True, help='Hash of a commit for which the data exist(s)')
    parser.add_argument('--user', required='--token' in sys.argv, help='Username for the labeler')
    parser.add_argument('--token', required=False, help='Token for the user, to grab info about the labeler')

    args = parser.parse_args()

    user_info = {}
    if args.token is not None:
        user_info = get_user_info(args.user, args.token)
    elif args.user is not None:
        user_info['username'] = args.user

    if args.data.startswith(args.repo):
        data = args.data[len(args.repo):]
        if data.startswith('/'):
            data = data[1:]
    else:
        data = args.data

    data_fullpath = args.repo + '/' + data
    print(data_fullpath)
    if os.path.isdir(data_fullpath):
        data = [os.path.join(data, l) for l in os.listdir(data_fullpath) if is_image(l)]
    else:
        data = [data]


    for d in data:
        gen_labelstudio_json(d, args.repo, args.commit, user_info)


if __name__ == '__main__':
    main()





