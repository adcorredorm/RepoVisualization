import requests 
import os
import json
import collections
from datetime import datetime, timezone
from dateutil.parser import parse

from env import URL, TOKEN

org_URL = URL
main_folder = 'clone_folder'
today = datetime.today()
today = today.replace(tzinfo = timezone.utc)

def get_data(url):
    headers = {'Authorization': f'token {TOKEN}'}
    return requests.get(url=url, headers=headers).json()

def time_to_str(time):
    return parse(time).strftime('%Y-%m-%d')

def days_since_updated(time):
    try:
        return (today - parse(time)).days 
    except:
        return -1

def effective_lines(lines, days, factor=0.999):
    return int(lines * (factor)**days)

if __name__ == '__main__':
    
    data = {}
    data_org = {
        'total_repos': 0,
        'total_lines': 0,
        'effective_lines': 0,
        'contributors': set()
    }

    repos = get_data(org_URL) 
    data_org['total_repos'] = len(repos)

    for repo in repos:
        data[repo['name']] = {
            'name': repo['name'],
            'owner': repo['owner']['login'],
            'description': repo['description'],
            'branches_url': repo['branches_url'].split('{')[0],
            'contributors_url': repo['contributors_url'],
            'languages_url': repo['languages_url'],
            'clone_url': repo['clone_url'],
            'created': time_to_str(repo['created_at']),
            'updated': time_to_str(repo['updated_at']),
            'days_since_updated': days_since_updated(repo['updated_at']),
            'default_branch': repo['default_branch'],
            'total_lines': 0,
            'effective_lines': 0,
            'branches': [],
            'contributors': [],
            'languages': [],
            'files': []
        }
    
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    for repo in data:
        folder = '{}/{}'.format(main_folder, repo)

        # Clonning the repository
        os.system('git clone {} {}'.format(data[repo]['clone_url'], folder))

        # Branches
        branches = get_data(data[repo]['branches_url'])
        for branch in branches:
            commit = get_data(branch['commit']['url'])
            last_update = commit['commit']['committer']['date']
            data[repo]['branches'].append({
                'name': branch['name'],
                'protected': bool(branch['protected']),
                'last_update': time_to_str(last_update),
                'days_since_updated': days_since_updated(last_update),
                'commit message': commit['commit']['message']
            })
        
        # Contributors
        contributors = get_data(data[repo]['contributors_url'])
        for cont in contributors:
            data[repo]['contributors'].append({
                'username': cont['login'],
                'url': cont['html_url'],
                'contributions': int(cont['contributions'])
            })
            data_org['contributors'].add(cont['login'])
        
        # Languages
        languages = get_data(data[repo]['languages_url'])
        total = sum(languages.values())
        for k, v in languages.items():
            data[repo]['languages'].append({
                'name': k,
                'percentage': '{:0.2f}%'.format((v / total)*100)
            })

        # Files
        files_by_lang = json.loads(os.popen(f'github-linguist {folder} --json').read())
        files = []
        for lang, fl in files_by_lang.items():
            for f in fl:
                with open(f'{folder}/{f}') as file:
                    lines = len(file.readlines())
                data[repo]['total_lines'] += lines
                modifications = os.popen(f'git -C {folder} log --pretty="format:%ci" {f}').read().split('\n')
                last_update = modifications[0] if len(modifications) > 0 else None
                file_info = {
                    'name': f,
                    'lines': lines,
                    'updates': len(modifications),
                    'last_update': time_to_str(last_update),
                    'days_since_updated': days_since_updated(last_update),
                    'language': lang
                }
                data[repo]['files'].append(file_info)
        
        ef_lines = effective_lines(data[repo]['total_lines'], data[repo]['days_since_updated'])
        data[repo]['effective_lines'] = ef_lines

        data_org['total_lines'] += data[repo]['total_lines']
        data_org['effective_lines'] += ef_lines
        
        with open("data.json", "w+") as outfile:  
            json.dump(data, outfile, indent=2) 
        
        # break

    data_org['contributors'] = list(data_org['contributors'])
    sorted_data = sorted(data.items(), key= lambda kv: kv[1]['effective_lines'], reverse=True)
    sorted_data = collections.OrderedDict(sorted_data)

    final_data = {'org': data_org}
    final_data = final_data | sorted_data
    with open("data.json", "w+") as outfile:  
        json.dump(final_data, outfile, indent=2) 
