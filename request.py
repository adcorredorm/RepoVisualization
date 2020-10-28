import requests 
import os
import json

org_URL = 'https://api.github.com/orgs/uapa-team/repos'
main_folder = 'clone_folder'

def get_data(url):
    headers = {'Authorization': 'token 4fd92298adbc61efb4296a3cf8940db490d449cc'}
    return requests.get(url=url, headers=headers).json()

if __name__ == '__main__':

    data = {}

    repos = get_data(org_URL) 

    for repo in repos:
        data[repo['name']] = {
            'name': repo['name'],
            'owner': repo['owner']['login'],
            'description': repo['description'],
            'branches_url': repo['branches_url'].split('{')[0],
            'contributors_url': repo['contributors_url'],
            'clone_url': repo['clone_url'],
            'created': repo['created_at'],
            'updated': repo['updated_at'],
            'branches': [],
            'default_branch': repo['default_branch'],
            'total_lines': 0,
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
            data[repo]['branches'].append({
                'name': branch['name'],
                'protected': bool(branch['protected']),
                'last_update': commit['commit']['committer']['date'],
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
        
        # Languages
        languages = os.popen(f'github-linguist {folder}').read().strip().split('\n')
        for lang in languages:
            p, l = lang.split('%')
            data[repo]['languages'].append({
                'name': l.strip(),
                'percentage': float(p)
                })

        # Files
        files = os.popen(f'git -C {folder} ls-files').read().strip().split('\n')
        for f in files:
            lines = int(os.popen('wc -l {}/{}/{}'.format(
                main_folder, repo, f)).read().split(' ')[0])
            
            data[repo]['total_lines'] += lines

            modifications = os.popen(f'git -C {folder} log --pretty="format:%ci" {f}').read().split('\n')

            language = os.popen(f'github-linguist {folder}/{f}').read()
            language = language.split('language:')[1].strip().split('\n')[0]

            file_info = {
                'name': f,
                'lines': lines,
                'updates': len(modifications),
                'last_update': modifications[0] if len(modifications) > 0 else None,
                'language': language
            }
            data[repo]['files'].append(file_info)
        
        break
    
    with open("data.json", "w+") as outfile:  
        json.dump(data, outfile, indent=2) 
