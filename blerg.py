#!/usr/bin/env python
"""
This is the blob of python that powers my blog thing.
"""

# Config processing
import yaml

# Processing RST and processing files
from jinja2 import Environment, FileSystemLoader
from docutils.core import publish_parts

# Creating final build files
from os import getcwd, path, makedirs
from shutil import copy2, copytree
from time import process_time

# HTTP Server Handling
from http.server import HTTPServer, SimpleHTTPRequestHandler
from sys import argv
from os import walk, stat, chdir
from subprocess import Popen

# RSS Feed
from feedgen.feed import FeedGenerator

# Signal Handling
from sys import exit
from signal import signal, SIGINT


metadata_file = 'metadata.yml'

# I decided to make this global. I think there are a few hacks I need to get
# rid of becuase of this change. If something doesn't make sense and looks
# like a hack it's becuase this wasn't global initially.
try:
    with open(metadata_file, 'r') as f:
        conf = yaml.load(f)
except FileNotFoundError:
    print('metadata.yml not found')
#    print('Try running `blerg.py init`')
    exit()

for element in conf:
    try:
        conf[element].replace('/content','').replace('content/','')
    except:
        pass

archive_cutoff = conf['archive_cutoff']
archive_url = '/archive/'


# Signal Handling
def handler(signum, frame):
    """
    Handles a given signal by exiting.
    """
    print('exiting '+argv[0]+'...')
    exit()

signal(SIGINT, handler)


def collect():
    """
    Collects a site's metadata.
    """
    pages = []
    for val in conf['content']['pages']:
        pages.append(collect_single(val))
    return pages


def collect_single(info=None):
    """
    Collects metada for a given rst file.
    """
    ret_val = {}
    for k, v in list(info.items()):
        ret_val['title'] = k
        ret_val['url'] = '/posts/'+v.replace('.rst','')+'/'
        ret_val['filename'] = conf['content']['source_dir']+v
    return ret_val


def render():
    """
    Renders the site.
    """
    start_time = process_time()

    nav = collect()
    navbar = []

    # Render main pages content
    for i in nav:
        if i['filename'] != conf['special_pages']['homepage']['filename']:
            navbar.append(i)
    for e in nav:
        e['content'] = render_single(filename=e['filename'],
                                     title=e['title'],
                                     url=e['url'],
                                     page_template=conf['content']['template'],
                                     navigation=navbar)

    # Render Special Pages
    for page in conf['special_pages']:
        p = conf['special_pages'][page]
        render_single(filename=p['filename'],
                      title=p['title'],
                      url=p['url'],
                      page_template=p['template'],
                      navigation=navbar)
    for sf in conf['special_files']:
        f = conf['special_files'][sf]
        try:
            copy2(f['location'], f['destination'])
        except IsADirectoryError:
            try:
                copytree(f['location'], f['destination'])
            except FileExistsError:
                pass

    # Render RSS feed
    try:
        generate_rss(nav)
    except KeyError as err:
        print('Key not found. Please add: ' + str(err) + ' to metadata.')

    print('Rendered site in {:0.4f} seconds'.format(process_time() - start_time))


def render_single(filename=None, title=None, url=None, page_template=None,\
                  navigation=None):
    """
    Renders a given rst file.
    """
    try:
        with open(filename) as f:
            file_content = publish_parts(f.read(), writer_name='html')
    except:
        file_content = ''

    title = title 
    body = file_content
    archive_url='/archive/'

    for element in body:
        body[element].replace('\\n','')

    with open(page_template, 'r') as f:
        loader = FileSystemLoader(getcwd())
        env = Environment(loader=loader)
        template = env.get_template(page_template)
        page = template.render(title=title,
                               article=body,
                               style='style.css',
                               jquery='jquery-1.11.3.min.js',
                               archive_url=archive_url,
                               archive_cutoff=archive_cutoff,
                               filename=filename,
                               navigation=navigation)

    try:
        makedirs('./build/'+url)
    except:
        pass
    with open('./build/'+url+'index.html', 'w') as f:
        f.write(page)

    return file_content


def server():
    """
    Runs a http server that reloads when content is updated.
    """
    with Popen(['blerg.py', 'watch']):
        cwd = getcwd()
        chdir(cwd+'/build/')
        http = HTTPServer(('127.0.0.1', conf['server_port']), SimpleHTTPRequestHandler)
        print('Serving on http://127.0.0.1:'+str(conf['server_port']))
        http.serve_forever()

def watch():
    """
    Rebuilds the website if it needs to be rebuilt.
    """
    render()
    cwd = getcwd()
    while True: 
        changed = things_changed(cwd)
        if changed:
            print(changed+' was updated. Rebuilding...')
            chdir(cwd)
            render()


def things_changed(directory=None):
    """
    Checks if content in /templates/ or /content/ are newer than the rendered
    versions. Returns true if they are.
    """
    try:
        ref_statbuf = stat(directory+'/build/index.html')
    except FileNotFoundError:
        return directory

    for root, dirs, files in walk(directory):
        for name in files:
            if (not name.startswith('.'))\
            and (name.endswith('metadata.yml')\
            or root.startswith(directory+'/content')\
            or root.startswith(directory+'/templates')):
                statbuf = stat(root+'/'+name)
                if statbuf.st_mtime > ref_statbuf.st_mtime:
                    return root+'/'+name
    return False


def print_help():
    """
    Prints a simple help menu for the user
    """
    print('Blerg Engine')
    print('Commands:')
    print('    blerg.py         : builds website')
    print('    blerg.py server  : starts an auto-updating server')
    print('    blerg.py help    : this help text')


def generate_rss(pages_info=None):
    fg = FeedGenerator()
    fg.id(conf['base_url'])
    fg.title(conf['title'])
    fg.author( {'name':conf['author'],'email':conf['email']} )
    fg.link( href=conf['base_url'], rel='alternate' )
    fg.subtitle(conf['description'])
    fg.link( href=conf['base_url']+'/rss.xml', rel='self' )
    fg.language('en')
    for post in pages_info:
        fe = fg.add_entry()
        fe.id('http://blog.elijahcaine.me/'+post['url'])
        fe.title(post['title'])
        fe.author( {'name':conf['author'],'email':conf['email']} )
        fe.link( href=conf['base_url']+post['url'], rel='alternate' )
        fe.description( post['content']['fragment'] )
    rssfeed  = fg.rss_str(pretty=True)
    fg.rss_file('build/'+conf['rss_feed'])
    return rssfeed


if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == 'serve' or argv[1] == 'server':
            server()
        elif argv[1] == 'watch':
            watch()
        elif argv[1] == 'init':
            try:
                quickstart_init(argv[2])
            except:
                quickstart_init()
        elif argv[1] == 'help':
            print_help()
    else:
        render()
