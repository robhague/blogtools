#!/usr/bin/env python

"""
An ad-hoc script to extract my pre-2008 blog posts from the generated
HTML and output them in Jekyll format.

This script is not an example of good style, nor does it attempt to be
general. It was written quickly to do the job at hand. However, it may
be useful as a source of ideas if you're trying to do a similar
one-time migration.

Error handing is minimal, and there are surely unidentified bugs. It's
unlikely to format your hard drive, but back up your data before
running the script on it.
"""

import codecs
import os
import os.path
import shutil
import sys
import re

from bs4 import BeautifulSoup

def list_numeric(path):
  """Find directory entries with numeric names (corresponding to date
  indices)."""
  return (f for f in os.listdir(path) if re.match(r'^\d+$', f))

def find_files(top):
  """Find all date-based paths below the top directory."""
  for year in list_numeric(top):
    yearpath = os.path.join(top, year)
    for month in list_numeric(yearpath):
      monthpath = os.path.join(yearpath, month)
      for day in list_numeric(monthpath):
        yield (year, month, day)

def get_posts(soup):
  """Find the individual posts within a page represented by a
  BeautifulSoup object. This is done by finding the grandparent of each
  TD with a grey background (seriously; the source HTML was not
  semantic)."""
  headers = soup.find_all('td', bgcolor='#eeeeee', align='left')
  return [h.parent.parent for h in headers]

def get_title_and_body(post):
  """Extract the title and body based on known positions."""
  tds = post.find_all('td')
  return (tds[0].h2.text, tds[2])

def post_time(post):
  """Extract the post time, as a string."""
  footer = post.find_all('span', 'storyfooter')[0]
  return footer.text.strip().split(' ')[0]

def local_url(url):
  """Is the URL an internal reference?"""
  return (not url.startswith('mailto:') and (
    (not url.startswith('http://') or ('rho.org.uk' in url))))

def find_local_links(tags):
  """Return all local links (as BS tags)."""
  for link in tags.find_all('a'):
    url = link['href']
    if local_url(url): yield link

def find_local_images(tags):
  """Return all local images (as BS tags)."""
  for img in tags.find_all('img'):
    url = img['src']
    if local_url(url):
      yield img

def post_filename(year, month, day, title):
  """Return the filename for the post for a given date and title."""
  post_name = re.sub('[^A-Za-z_0-9]+', '_', title[:20].lower()).strip('_')
  return '-'.join([year, month, day, post_name]) + '.html'

def getdir(*components):
  """Returns a directory based on the given path components, creating it
  if necessary."""
  path = os.path.join(*components)
  try:
    os.makedirs(path)
  except:
    pass
  return path

if __name__ == '__main__':
  # Take the top of the archive tree and the results directory as
  # exactly two command line arguments.
  top, target = sys.argv[1], sys.argv[2]

  # Create a directory for the posts (as opposed to assets)
  postdir = getdir(target, '_posts')

  # Iterate over each daily index page
  for y,m,d in find_files(top):
    f = open(os.path.join(top,y,m,d,'index.html'))
    soup = BeautifulSoup(f)

    # Iterate over posts
    for p in get_posts(soup):
      title, bodytags = get_title_and_body(p)
      destfile = os.path.join(target, '_posts', post_filename(y,m,d,title))
      
      # Record local links for manual fixing
      for link in find_local_links(bodytags):
        link['href'] = 'FIXME:'+link['href']
      
      # Fix up images
      for img in find_local_images(bodytags):
        # Images are saved into a date-based directory directly
        # reflecting their final location.
        imgdir = getdir(y, m, d)
        oldpath = os.path.join(top, img['src'][1:])
        newpath = os.path.join(imgdir, os.path.basename(img['src']))
        shutil.copyfile(oldpath, os.path.join(newpath))
        img['src'] = '{%xref ' + newpath + ' %}'

      # Create the destination file with YAML front matter.
      print destfile
      postfile = codecs.open(destfile, 'w', 'utf8')
      postfile.write('---\n')
      postfile.write('title: '+title+'\n')
      postfile.write('date: %s-%s-%s %s:00 +0000\n' % (y,m,d, post_time(p)))
      postfile.write('layout: post\n')
      postfile.write('---\n')

      # Finally, write the HTML content of from the body of the post
      for t in bodytags:
        postfile.write(unicode(t))
