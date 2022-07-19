from urllib import response
import requests
import json
import git
import shutil
import os
import datetime
import sys
from urllib.parse import quote
from git import GitError, Repo


def git_clone(bit_bucket_username, bit_bucket_token, bit_bucket_repo_url) : 
    ## This function clones the repository which stores the backup of our dashboard
    try:
        local_repo_path = "."
        git.Git(local_repo_path).clone(("https://" + bit_bucket_username + ":" + bit_bucket_token + "@" + bit_bucket_repo_url), branch = 'master')
    except GitError as error :
        print (error)


def backup_grafana_dashboard_json(bit_bucket_repo_name):
    ## This function takes a backup of dashboard which were changes since the last commit
    source_directory = './JSON'
    source_files = os.listdir(source_directory)
    for filename in source_files:
        full_filename = os.path.join(source_directory, filename)
        if os.path.isfile(full_filename):
            shutil.copy(full_filename,bit_bucket_repo_name)
    
    repo = git.Repo(bit_bucket_repo_name)
    repo.git.add(all=True)
    try:
        repo.git.commit('-m', 'Backup-Grafana-Dashboards' + str(datetime.datetime.now()))
        origin = repo.remote(name='origin')
        origin.push()
    except GitError as e : 
        print(f"No files to commit, check error : ", e)
    finally:
        shutil.rmtree(bit_bucket_repo_name)


def fetch_grafana_folder() :
    ## We fetch a list of all the dashboards that are stored in .com expereince folder in orgid:148 in grafana and store that list in a JSON file
    try:
        grafana_token = os.getenv("grafana_token")
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + grafana_token
        } 
        params = {
            'folderIds' : '5325'
        }
        search_url = 'https://localhost:1010/api/search'
        grafana_response = requests.request('GET', url=search_url, headers=headers, params=params, verify=False)
        if grafana_response.status_code == 200 : 
            grafana_response = grafana_response.json()
            with open('grafana_folder.json', 'w') as grafana_folder: 
                json.dump(grafana_response, grafana_folder, indent=4)
        elif grafana_response.status_code == 401 : 
            print("Invalid or Expired API key")
            return sys.exit(1)  
        else :
            print("Error") 
            return sys.exit(1)
    except Exception as error :
        print(error)


def fetch_grafana_dashboard_id():
    ## This function reades a JSON file created by fetch_grafana_folder function and fetches the UID of the dashboard and 
    ## pass it as a parameter to fetch_grafana_dashboard_json function
    try:
        with open ('grafana_folder.json') as grafana_folder:
            grafana_data = json.load(grafana_folder)
            for i in grafana_data :
                uid = i["uid"]
                fetch_grafana_dashboard_json(uid)
    except Exception as error:
        print (error)

def fetch_grafana_dashboard_json(uid) : 
    ## This function fetches the JSON of dashboard whose UID is being passed into it
    try:
        uid_response = {}
        grafana_token = os.getenv("grafana_token")
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + grafana_token
        }
        dashboard_url = 'https://localhost:1010/api/dashboards/uid/' + uid
        grafana_response = requests.request('GET', url=dashboard_url, headers=headers, verify=False)
        uid_response = grafana_response.json()
        db_name = uid_response['meta']['slug']
        if not os.path.isdir('./JSON'):
            os.makedirs('./JSON')
        filename = 'JSON/' + db_name + '.json'
        with open (filename, 'w') as json_file:
            json.dump(uid_response, json_file, indent=4)
    except {Exception,json.JSONDecodeError} as error :
        print (error)

if __name__ == '__main__':
    ## Setting the environment variables we get from Jenkins Credentials Manager
    grafana_token = os.getenv("grafana_token")
    bit_bucket_username = os.getenv("bit_bucket_username")
    bit_bucket_token = quote(os.getenv("bit_bucket_token"))
    bit_bucket_repo_url = 'https://localhost:7990/scm/grafana-automation-test.git'
    bit_bucket_repo_name = 'grafana-automation-test'
    try:
        
        exit_code = fetch_grafana_folder()
        ## We continue further only if we do not get error returned from previous function, this will allow us to check grafana connectivity or expiry of the key
        if exit_code != 1:
            fetch_grafana_dashboard_id()
            git_clone(bit_bucket_username, bit_bucket_token, bit_bucket_repo_url)
            backup_grafana_dashboard_json(bit_bucket_repo_name)
        else :
            print ("Check Error")
    except Exception as error:
        print (error)