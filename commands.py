from urllib.parse import urlparse

from utils import *


def update():
    logger.info("Updating metadata...")
    with open("repo.txt") as repos:
        repos_list = repos.read().splitlines()

    # updating local metadata info
    with open("metadata.json", "w") as file:
        metadata = {}
        for server in repos_list:
            try:
                repo_data = open("repo.json")
                repo_db = json.load(repo_data)
                try:
                    repo_cert = repo_db[server]
                except KeyError:
                    repo_cert = requests.get(f"{server}repo/public_key").text
                    logger.info(f"{server} signature - \n{repo_cert}")
                    choice = input("You adding new server, would you like to accept its PGP public key? [y/n]")
                    if choice.lower() in ['yes', 'y']:
                        logger.info("Adding new signature...")
                        repo_db[server] = repo_cert
                        repo_data.close()
                        with open("repo.json", "w") as repo_data:
                            json.dump(repo_db, repo_data, indent=2)
                        logger.info(f"Done, added new signature for {server}")

                if verify_server(server):
                    data = requests.get(f"{server}repo/metadata")
                    logger.info(f"[GET] {server}repo/metadata {data.status_code}")
                    metadata.update(data.json())
                else:
                    logger.error(f"[GET] {server} PGP public key verification failure")
            except Exception:
                logger.error("Error while making request to repository, skipping...")

        logger.info("Writing updated info...")
        json.dump(metadata, file, indent=2)
        logger.info("Done")


def info(server):
    if server is None:
        logger.error("Error: you need to provide a server with -s")
        sys.exit()

    logger.info("Getting repository information...\n")

    info1 = requests.get(server + "repo/info").json()
    logger.info(f"Server: {info1['name']}")
    logger.info(f"Contact: {info1['email']}")
    logger.info(f"Version: {info1['version']}")
    logger.info(f"Amount of repositories on server: {info1['repositories']}\n")
    logger.info("Done")

def install(repo):
    if repo is None:
        logger.error("Error: you need to provide a repository to install with -r")
        sys.exit()

    logger.info("Searching repository in metadata...")
    with open("metadata.json") as file:
        metadata = json.load(file)

    try:
        repo_source = metadata[repo]["source"]
        repo_author = metadata[repo]["author"]
        repo_description = metadata[repo]["description"]
        repo_email = metadata[repo]["email"]
        repo_version = metadata[repo]["version"]
    except KeyError:
        logger.error("Error: repository not found in metadata. Try using 'sierepo update' for updating metadata info.")
        sys.exit()

    logger.info(f"Installing {repo} by {repo_author} - version {repo_version}")
    logger.info(f"Description -\n{repo_description}")
    logger.info(f"Contact author - {repo_email}")

    server = urlparse(repo_source)
    server = server._replace(path='').geturl() + "/"
    check_version(server)
    if verify_server(server):
        try:
            file = download_and_verify_file(repo_source, repo, server=server)
            logger.info("Unpacking package...")
            unpack_package(file)
            logger.info("Done! Package successfully installed.")
        except Exception:
            logger.error("Error: download failed, please try again later.")
    else:
        logger.error(f"[GET] {repo_source} PGP public key verification failure")
