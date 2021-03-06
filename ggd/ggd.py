#!/usr/bin/env python

import argparse
import os
import requests
import shutil
import subprocess
import sys
import tempfile
import urllib2
import yaml
import hashlib


recipe_urls = {
  "core": "https://raw.githubusercontent.com/arq5x/ggd-recipes/master/",
  "api": "https://api.github.com/repos/arq5x/ggd-recipes/git/trees/master?recursive=1"
  }


def _get_config_data(config_path):
  if config_path is None:
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'config.yaml')
  with open(config_path, 'r') as f:
    config = yaml.load(f.read())
  f.close()
  return config

def _get_sha1_checksum(filename, blocksize=65536):
  """
  Return the SHA1 checksum for a dataset.
  http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
  """
  hasher = hashlib.sha1()
  f = open(filename, 'rb')
  buf = f.read(blocksize)
  while len(buf) > 0:
    hasher.update(buf)
    buf = f.read(blocksize)
  return hasher.hexdigest()


def get_install_path(config_path):
  """
  Retrieve the  path for installing datasets from
  the GGD config file.
  """
  config = _get_config_data(config_path)
  return config['path']['root']


def set_install_path(data_path, config_path):
  """
  Change the path for installing datasets.
  """
  config = _get_config_data(config_path)
  # change the data path and update the config file
  config['path']['root'] = data_path
  with open(config_path, 'w') as f:
    f.write(yaml.dump(config, default_flow_style=False))
  f.close()


def register_installed_recipe(args, recipe_dict):
  """
  Add a dataset to the list of installed datasets 
  in the config file.
  """
  #config = AutoDict(_get_config_data(args.config))

  #if 'installed' not in config:
  #  config['installed']['recipe'] = args.recipe
  #print recipe_dict



def _get_recipe(args, url):
  """
  http://stackoverflow.com/questions/16694907/\
  how-to-download-large-file-in-python-with-requests-py
  """
  print >> sys.stderr, "searching for recipe: " + args.recipe + "...",

  # hanndle core URL and http:// and ftp:// based cookbooks
  if args.cookbook is None or "file://" not in args.cookbook:
    r = requests.get(url, stream=True)
    if r.status_code == 200:
      print >> sys.stderr, "ok"
      return r.text
    else:
      print >> sys.stderr, "failed"
      return None
  #responses library doesn't support file:// requests
  else:
    r = urllib2.urlopen(url)
    if r.getcode() is None:
      print >> sys.stderr, "ok"
      return r.read()
    else:
      print >> sys.stderr, "failed"
      return None



def _run_recipe(args, recipe):
  """
  Execute the contents of a YAML-structured recipe.
  """

  # bash, etc.
  recipe_version = recipe['attributes'].get('version')
  # used to validate the correctness of the dataset
  recipe_sha1s = recipe['attributes'].get('sha1')

  if args.region is None:
    recipe_type = recipe['recipe']['full']['recipe_type']
    # specific commnads to execute recipe.
    recipe_cmds = recipe['recipe']['full']['recipe_cmds']
    # the output file names for the recipe.
    recipe_outfiles = recipe['recipe']['full']['recipe_outfiles']
  else:
    if 'region' in recipe['recipe']:
      # bash, etc.
      recipe_type = recipe['recipe']['region']['recipe_type']
      # specific commnads to execute recipe.
      recipe_cmds = recipe['recipe']['region']['recipe_cmds']
      # the output file names for the recipe.
      recipe_outfiles = recipe['recipe']['region']['recipe_outfiles']
    else:
      print >> sys.stderr, "region queries not supported for " + args.recipe

  # use os.path.expanduser to expand $HOME, etc.
  install_path = os.path.expandvars(get_install_path(args.config))
  if not os.path.exists(install_path):
    os.makedirs(install_path)


  print >> sys.stderr, "executing recipe:"
  for idx, cmd in enumerate(recipe_cmds):
    out_file = os.path.join(install_path, recipe_outfiles[idx])
    f = open(out_file, 'w')
    if recipe_type == 'bash':
      if args.region is not None:
        cmd += ' ' + args.region

      counter = 0
      p = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
      while True:
        line = p.stdout.readline()
        counter += 1
        if not line:
          print >> sys.stderr, "."
          break
        if counter % 1000 == 0:
          if counter % 40000 != 0:
            print >> sys.stderr, ".",
          else:
            print >> sys.stderr, "."
        f.write(line)

      #if ret: # return non-zero if failure
      #    print >> sys.stderr, "failure installing " + args.recipe
    else:
      print >> sys.stderr, "recipe_type not yet supported"
    f.close()


    # validate the SHA1 checksum
    if isinstance(recipe_sha1s, list):
      recipe_sha1 = recipe_sha1s[idx]
    else:
      recipe_sha1 = recipe_sha1s

    if recipe_sha1 is not None and args.region is None:
      print >> sys.stderr, \
        "validating dataset SHA1 checksum for " + out_file + "...",
      observed_sha1 = _get_sha1_checksum(out_file)
      if observed_sha1 == recipe_sha1:
        print >> sys.stderr, "ok (" + observed_sha1 + ")"
      else:
        print >> sys.stderr, "failed (obs: " + observed_sha1 + ") != (exp: " + recipe_sha1
        print >> sys.stderr, "failure installing " + args.recipe + "."
        print >> sys.stderr, "perhaps the connection was disrupted? try again?"

  return True


def install(parser, args):
  """
  Install a dataset based on a GGD recipe
  """
  recipe = args.recipe

  if args.cookbook is None:
    recipe_url = recipe_urls['core'] + recipe + '.yaml'
  else:
    recipe_url = args.cookbook + recipe + '.yaml'

  # get the raw YAML string contents of the recipe
  recipe = _get_recipe(args, recipe_url)

  if recipe is not None:
    # convert YAML to a dictionary
    recipe_dict = yaml.load(recipe)
    if _run_recipe(args, recipe_dict):
      
      # TO DO
      #register_installed_recipe(args, recipe_dict)
      
      print >> sys.stderr, "installed " + args.recipe
    else:
      print >> sys.stderr, "failure installing " + args.recipe
  else:
    print >> sys.stderr, "exiting."


def list_recipes(parser, args):
  """
  List all available datasets
  """
  request = requests.get(recipe_urls['api'])
  tree = request.json()['tree']
  for branch in tree:
    if ".yaml" in branch["path"]:
      print branch['path'].rstrip('.yaml')


def search_recipes(parser, args):
    """
    Search for a recipe
    """
    recipe = args.recipe
    request = requests.get(recipe_urls['api'])
    tree = request.json()['tree']
    matches = [branch['path'] for branch in tree if recipe in branch['path'] and ".yaml" in branch["path"]]
    if matches:
        print "Available recipes:"
        print "\n".join(match.rstrip('.yaml') for match in matches)
    else:
        print >> sys.stderr, "No recipes available for {}".format(recipe)


def setpath(parser, args):
  """
  Set the path to use for storing installed datasets
  """
  set_install_path(args.path, args.config)


def getpath(parser, args):
  """
  Get the path used for storing installed datasets
  """
  print os.path.expandvars(get_install_path(args.config))


def main():

  # create the top-level parser
  parser = argparse.ArgumentParser(prog='ggd')
  parser.add_argument("-v", "--version", help="Installed ggd version",
                      action="version",
                      version="alpha")
  subparsers = parser.add_subparsers(title='[sub-commands]', dest='command')

  # parser for install tool
  parser_install = subparsers.add_parser('install',
    help='Install a dataset based on a recipe')
  parser_install.add_argument('recipe',
    metavar='STRING',
    help='The GGD recipe to use.')
  parser_install.add_argument('--region',
    dest='region',
    metavar='STRING',
    required=False,
    help='A genomic region to extract. E.g., chr1:100-200')
  parser_install.add_argument('--cookbook',
    dest='cookbook',
    metavar='STRING',
    required=False,
    help='A URL to an alternative collection of '
    'recipes that follow the GGD ontology')
  parser_install.add_argument('--config',
    dest='config',
    metavar='STRING',
    required=False,
    help='Absolute location to config file')
  parser_install.set_defaults(func=install)

  # parser for list tool
  parser_list = subparsers.add_parser('list',
    help='List available recipes')
  parser_list.set_defaults(func=list_recipes)

  # parser for search tool
  parser_search = subparsers.add_parser('search',
    help='Search available recipes')
  parser_search.add_argument('recipe',
    metavar='STRING',
    help='The GGD recipe to search.')
  parser_search.set_defaults(func=search_recipes)

  # parser for setpath tool
  parser_setpath = subparsers.add_parser('setpath',
    help='Set the path to which datasets should be installed.')
  parser_setpath.add_argument('--path',
    dest='path',
    metavar='STRING',
    help='The data path to use.')
  parser_setpath.add_argument('--config',
    dest='config',
    metavar='STRING',
    required=False,
    help='Absolute location to a specific config file')
  parser_setpath.set_defaults(func=setpath)

  # parser for getpath tool
  parser_getpath = subparsers.add_parser('where',
    help='Display the path in which datasets are installed.')
  parser_getpath.add_argument('--config',
    dest='config',
    metavar='STRING',
    required=False,
    help='Absolute location to a specific config file')
  parser_getpath.set_defaults(func=getpath)

  # parse the args and call the selected function
  args = parser.parse_args()

  try:
    args.func(parser, args)
  except IOError, e:
       if e.errno != 32:  # ignore SIGPIPE
           raise

if __name__ == "__main__":
    main()
