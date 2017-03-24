#!/usr/bin/env python3                                                                  
# License: GPLv2+
'''                                                                                     
File containing the gitlab_to_bitbucket.py python script part of the gitlab-to-bitbucket package.

Clone all projects from GitLab and recreate them on Bitbucket and push clone and tags to Bitbucket.

:author: Brookins Consulting (info@brookinsconsulting.com)
:organization: Brookins Consulting
:copyright: Copyright (C) Brookins Consulting. All rights reserved.
:license: For full copyright and license information view LICENSE and COPYRIGHT.md file distributed with this source code.
:package: gitlab-to-bitbucket
:date: 03/22/2017
'''

################################################################################
# Imports

import sys
import os
import sh
import argparse
import gitlab
import logging
import subprocess
import random, string

from optparse import OptionParser
from subprocess import Popen, PIPE

#import getpass
#import re
#import tempfile

# Version
__version__ = '0.1.2'

################################################################################
# Function: randomstring

def randomstring(length):
   return ''.join(random.choice(string.digits + '_-' + string.ascii_lowercase) for i in range(length))

################################################################################
# Function: main

def main(argv=None):
    '''
    Process the command line arguments, connect to gitlab, fetch projects,
    checkout / clone each repository, create coresponding repository on Bitbucket,
    push repository to Bitbucket, push all tags to Bitbucket, remove tmp clone files.
    :param argv: List of arguments, as if specified on the command-line.
                 If None, ``sys.argv[1:]`` is used instead.
    :type argv: list of str
    '''
    ################################################################################
    #
    # Get command line arguments
    parser = argparse.ArgumentParser(
        description="Transfer all projects/repositories from GitLab to Bitbucket. \
                     Notes: This script assumes you have your SSH key \
                            registered with both GitLab and Bitbucket.\
                            This script assumes you have installed AND configured all requirements. \
                            This script assumes you want this completed quickly. \
                            Which is why it is 'life so cray cray basic'.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        conflict_handler='resolve')
    parser.add_argument('-hau', '--host-alias', action='store_true',
                             dest="host_alias_use", default=False, required=False,
                             help="Flag indicating Use of Repository Storage Host Alias used for ssh clone operations \
                             Used to provide for multiple ssh host aliases. \
                             Optional.")
    parser.add_argument('-fa', '--fetch-all', action='store_true',
                             dest="fetch_all", default=False, required=False,
                             help="Flag indicats the fetching of all GitLab projects which can take much longer and apear to stall the program \
                             Used to provide for control over importing only the first page of projects or all projects \
                             Semi-Required. Defaults to False.")
    parser.add_argument('-P', '--page_size',
                        help='When retrieving result from GitLab, how many \
                              results should be included in a given page? \
                              Optional. Defaults to 20. Maximum is 100.',
                        type=int, default=20)
    #parser.add_argument('-S', '--skip_existing',
    #                    help='Do not update existing repositories and just \
    #                          skip them.',
    #                    action='store_true')
    parser.add_argument('-t', '--token', required=True,
                        help='The private GitLab API token to use for \
                              authentication. Either this or username and \
                              password must be set.')
    parser.add_argument('-u', '--host-url', required=False,
                        help='The GitLab Host Url used for GitLab operations \
                              Used to provide for private GitLab installation instance usage. \
                              Optional. Defaults to https://gitlab.com')
    parser.add_argument('-ha', '--host', required=False,
                        help='The GitLab Host Name used for ssh clone operations \
                              Used to provide for multiple ssh host aliases. \
                              Optional. Defaults to gitlab.com')
    parser.add_argument('-hap', '--host-alias-prefix', required=False,
                        help="The GitLab Host Alias used for ssh clone operations \
                              Used to provide for multiple ssh host aliases. \
                              Optional. Defaults to '-as-'")
    #parser.add_argument('-u', '--username',
    #                    help='The username to use for authentication, if token\
    #                          is unspecified.')
    #parser.add_argument('-p', '--password',
    #                    help='The password to use to authenticate if token is \
    #                          not specified. If password and token are both \
    #                          unspecified, you will be prompted to enter a \
    #                          password.')
    parser.add_argument('-v', '--verbose',
                        help='Print more status information. For every ' +
                             'additional time this flag is specified, ' +
                             'output gets more verbose. Detailed output starts with -vv',
                        default=0, action='count')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {0}'.format(__version__))

    ################################################################################
    #

    # Parse command line arguments
    args = parser.parse_args(argv)

    # Convert verbose flag to actually logging level
    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = log_levels[min(args.verbose, 2)]

    # Make warnings from built-in warnings module get formatted more nicely
    logging.captureWarnings(True)
    logging.basicConfig(format=('%(asctime)s - %(name)s - %(levelname)s - ' +
                                '%(message)s'), level=log_level)

    ################################################################################
    #

    # Define Default Parameters
    verbose = args.verbose
    tmp_path = "/tmp/gitlab_to_bitbucket_import_" + randomstring(64) + "/"
    token = args.token
    gitlab_fetch_all_projects = args.fetch_all
    gitlab_page_item_count = max(100, args.page_size)
    gitlab_instance_url = args.host_url
    default_host_name = args.host
    host_alias_use = args.host_alias_use
    host_alias_prefix = args.host_alias_prefix
    gitlab_name = 'gitlab'
    bitbucket_name = 'bitbucket'
    bitbucket_host = bitbucket_name + '.org'

    ################################################################################
    #

    # Test for default parameters
    if default_host_name == None:
        default_host_name = 'gitlab.com'
    else:
        if verbose >= 2:
            print('Using host: ' + default_host_name)

    if gitlab_instance_url == None:
        gitlab_instance_url = 'https://gitlab.com'
    else:
        if verbose >= 2:
            print('Using gitlab instance url: ' + gitlab_instance_url)

    if host_alias_use == None:
        use_host_alias = False
    else:
        use_host_alias = True

    if use_host_alias == True and host_alias_prefix == None:
        host_alias_prefix = '-as-'
        if verbose >= 2:
            print('Using host alias prefix: ' + gitlab_name + host_alias_prefix + ' and ' + bitbucket_name + host_alias_prefix)
    elif use_host_alias == False and host_alias_prefix != None:
        use_host_alias = False

    ################################################################################
    #

    # Create temporary directory
    sh.mkdir(tmp_path)

    ################################################################################
    #

    # Authenticate with GitLab instance using private token
    if args.token:
        gl = gitlab.Gitlab(gitlab_instance_url, token)
    else:
        gl = None

    # Make an API request to create the gl.user object.
    # This is mandatory if you use the username/password authentication.
    gl.auth()

    ################################################################################
    #

    # Fetch all projects
    if gitlab_fetch_all_projects == True:
        if verbose >= 2:
            print('Fetching all GitLab projects...', file=sys.stderr)
        projects = gl.projects.owned(all=True, per_page=gitlab_page_item_count)
    else:
        if verbose >= 2:
            print('Fetching first page of GitLab projects...(limited)', file=sys.stderr)
        projects = gl.projects.owned(page=1, per_page=gitlab_page_item_count)

    if verbose >= 1:
        print('Processing GitLab projects...', file=sys.stderr)
    sys.stderr.flush()

    ################################################################################
    #

    # Iterate over gitlab list of projects / repositories
    for project in projects:
        if verbose >= 2:
            print('\n' + ('=' * 80) + '\n', file=sys.stderr)
        sys.stderr.flush()

        # Project repository information
        proj_name = project.name
        tmp_proj_path = tmp_path + proj_name
        proj_description = project.description
        proj_repo_visibility = project.visibility_level
        proj_ssh_url_to_repo = project.ssh_url_to_repo
        project_owner_name = project.owner.username

        if proj_description == None:
            proj_description = ''

        if use_host_alias == True:
            proj_ssh_url_to_repo = proj_ssh_url_to_repo.replace(default_host_name, gitlab_name + host_alias_prefix + project_owner_name)

        if verbose >= 0:
            print("Processing: " + proj_name)

        ################################################################################
        #

        # Clone repository in temporary directory
        if not os.path.exists(tmp_proj_path):
            if verbose >= 1:
                print("Cloning repository")

            if verbose >= 1:
                print(sh.pwd())

            sh.cd(tmp_path)
            sh.git.clone(proj_ssh_url_to_repo)

            if verbose >= 2:
                print("Clone completed")

            sh.cd("../")

        if verbose >= 1:
            print("Creating repository on Bitbucket")

        sh.cd(tmp_proj_path)

        if verbose >= 1:
            print(sh.pwd())

        ################################################################################
        #

        # Create Bitbucket repository
        try:
            if proj_repo_visibility == "0":
                sh.git.bb("--private --description=" + proj_description, 'create')
            else:
                sh.git.bb("--description=" + proj_description, 'create')

            # Fix remote for Bitbucket to use host alias
            if use_host_alias == True:
                cmd_fetch_submodule = "git remote -v|grep '" + bitbucket_host + "'|grep \(fetch\)| cut -f 2 | cut -d' ' -f1|tr -d '\n'"
                p = Popen(cmd_fetch_submodule , shell=True, stdout=PIPE, stderr=PIPE)
                # print("Return code: ", p.returncode)
                destination_proj_ssh_url_to_repo, err = p.communicate()
                destination_proj_ssh_url_to_repo = 'ssh://' + destination_proj_ssh_url_to_repo.decode('UTF-8').replace(bitbucket_host + ':', bitbucket_name + host_alias_prefix + project_owner_name + '/')

                sh.git("remote", "remove", bitbucket_name)
                sh.git.remote("add", bitbucket_name, destination_proj_ssh_url_to_repo)

            ################################################################################
            #

            # Push content to bitbucket repository
            if verbose >= 1:
                print("Pushing repository")
                if verbose >= 2:
                    print(sh.pwd())
            sh.git.push("--all", "--repo", bitbucket_name)

            if verbose >= 1:
                print("Pushing tags")
            sh.git("push", "--tags", "--repo", bitbucket_name)
        except sh.ErrorReturnCode_1:
            if verbose >= 1:
                print('Failed. Repository already exists.', file=sys.stderr)

        if verbose >= 1:
            print(sh.pwd())

        sh.cd('../')

        ################################################################################
        #

        # Disk Temporary Files Cleanup : Remove repository checkout
        sh.rm("--recursive", "--force", proj_name)

        sh.cd('../')
        if verbose >= 1:
            print(sh.pwd())

    ################################################################################
    #

    # Disk Temporary Directory Removal
    sh.rm("--recursive", "--force", tmp_path)

    if verbose >= 2:
        print('\n' + ('=' * 80) + '\n', file=sys.stderr)

    print("Import completed")

################################################################################
#

# Execute program main
if __name__ == '__main__':
    main()

################################################################################
# fin
