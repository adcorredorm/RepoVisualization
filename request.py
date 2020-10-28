import requests 
import os
import json
import ghlinguist as ghl

org_URL = 'https://api.github.com/orgs/uapa-team/repos'
main_folder = 'clone_folder'

def get_data(url):
    return requests.get(url=url).json()

if __name__ == '__main__':

    data = {}

    repos = get_data(org_URL) 

    for repo in repos:
        data[repo['name']] = {
            'name': repo['name'],
            'owner': repo['owner']['login'],
            'description': repo['description'],
            'branches_url': repo['branches_url'].split('{')[0],
            'languages_url': repo['languages_url'],
            'contributors_url': repo['contributors_url'],
            'commits_url': repo['commits_url'].split('{')[0],
            'clone_url': repo['clone_url'],
            'created': repo['created_at'],
            'updated': repo['updated_at'],
            'language': repo['language'],
            'default_branch': repo['default_branch'],
            'total_lines': 0,
            'files': []
        }
    
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    for repo in data:
        folder = '{}/{}'.format(main_folder, repo)
        #os.system('git clone {} {}'.format(data[repo]['clone_url'], folder))
        os.system('cd {}'.format(folder))
        files = os.popen(f'git -C {folder} ls-files').read().split('\n')[:-1]
        for f in files:
            lines = int(os.popen('wc -l {}/{}/{}'.format(
                main_folder, repo, f)).read().split(' ')[0])
            
            data[repo]['total_lines'] += lines

            modifications = os.popen(f'git -C {folder} log --pretty="format:%ci" {f}').read().split('\n')

            print(f, ghl.linguist(f'{folder}/{f}').language.name)

            file_info = {
                'name': f,
                'lines': lines,
                'updates': len(modifications),
                'last_update': modifications[0] if len(modifications) > 0 else None
            }
            data[repo]['files'].append(file_info)
        
        break




    
    with open("data.json", "w+") as outfile:  
        json.dump(data, outfile, indent=2) 
