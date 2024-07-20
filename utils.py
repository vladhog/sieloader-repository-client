import base64
import io
import json
import logging
import os
import sys
import warnings
import tarfile

warnings.filterwarnings("ignore")

import pgpy
import requests
from tqdm import tqdm

logger = logging.getLogger("SIERRA Repository Client")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

version = "0.1"
github = ""

# checking files for sure
# checking metadata file
try:
    with open("metadata.json") as file:
        tmp = json.load(file)
except Exception:
    with open("metadata.json", "w") as file:
        json.dump({}, file, indent=2)

# checking repos data information
try:
    with open("repo.json") as file:
        tmp = json.load(file)
except Exception:
    with open("repo.json", "w") as file:
        json.dump({}, file, indent=2)

# checking repos list
try:
    with open("repo.txt") as file:
        tmp = file.read()
except Exception:
    with open("repo.txt", "w") as file:
        file.write("https://sierra.vladhog.ru/")


def verify_server(server):
    try:
        cert = requests.get(f"{server}repo/public_key").text
        with open("repo.json") as file:
            data = json.load(file)
            if data[server] == cert:
                return True
            else:
                return False
    except Exception:
        return False


def check_version(server):
    data = requests.get(f"{server}repo/info").json()
    if data['version'] != version:
        logger.error(
            f"Your sierepo version dont much server version, please update sierepo client over our github\n{github}")
        sys.exit()


def download_and_verify_file(repo_source, repo, verify=True, server=None):
    request = requests.get(repo_source, stream=True)
    try:
        os.mkdir(f"./addons/")
    except FileExistsError:
        pass
    try:
        os.mkdir(f"./addons/{repo}/")
    except FileExistsError:
        pass

    tmp_file = io.BytesIO()

    with open("metadata.json") as metadata:
        metadata = json.load(metadata)
        total_length = int(metadata[repo]['size'])

    bar = tqdm(desc=f"[GET] {repo_source}",
               total=total_length,
               unit="iB",
               unit_scale=True,
               unit_divisor=1024)
    for data in request.iter_content(chunk_size=1024):
        size = tmp_file.write(data)
        bar.update(size)

    tmp_file.seek(0)
    tmp_data = tmp_file.read()
    tmp_file.close()

    tmp_data = base64.b64decode(tmp_data)
    message = pgpy.PGPMessage.from_blob(tmp_data)

    if verify:
        # verifying message
        with open("repo.json") as repo_data:
            repo_data = json.load(repo_data)

        public_key, _ = pgpy.PGPKey.from_blob(base64.b64decode(repo_data[server]))
        signature = pgpy.PGPSignature.from_blob(base64.b64decode(requests.get(f"{repo_source}/signature").content))
        tmp = message
        tmp |= signature
        if not public_key.verify(tmp):
            logger.error("Error: failed to verify downloaded package signature")
            sys.exit()

    with open(f"{message.filename}", "wb") as file:
        file.write(message.message)
    return f"{message.filename}"


def unpack_package(file):
    with tarfile.open(file, 'r:xz') as package:
        package.extractall("./addons/")
    os.remove(file)

    # return f"addons/{repo}/data.tar.xz"
