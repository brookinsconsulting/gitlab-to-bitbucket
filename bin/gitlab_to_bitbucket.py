#!/usr/bin/env python3                                                                  
# License: GPLv2+
'''                                                                                     
File containing the gitlab_to_bitbucket.py python script part of the gitlab-to-bitbucket package.

Clone all projects from GitLab and recreate them on Bitbucket and push clone and tags to BitBucket.

:author: Brookins Consulting (info@brookinsconsulting.com)
:organization: Brookins Consulting
:copyright: Copyright (C) Brookins Consulting. All rights reserved.
:license: For full copyright and license information view LICENSE and COPYRIGHT.md file distributed with this source code.
:package: gitlab-to-bitbucket
:date: 03/22/2017
'''

import sys
import os
import sh
import argparse
import gitlab
import logging
import subprocess

#import getpass
#import re
#import tempfile

__version__ = '0.1.1'

def main(argv=None):
    '''
    Process the command line arguments, connect to gitlab, fetch projects,
    checkout / clone each repository, create coresponding repository on bitbucket,
    push repository to bitbucket, push all tags to bitbucket, remove tmp clone files.
    :param argv: List of arguments, as if specified on the command-line.
                 If None, ``sys.argv[1:]`` is used instead.
    :type argv: list of str
    '''
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
    parser.add_argument('gitlab_url',
                        help='The full URL to your GitLab instance.')
    parser.add_argument('-P', '--page_size',
                        help='When retrieving result from GitLab, how many \
                              results should be included in a given page?.',
                        type=int, default=20)
    parser.add_argument('-S', '--skip_existing',
                        help='Do not update existing repositories and just \
                              skip them.',
                        action='store_true')
    parser.add_argument('-t', '--token',
                        help='The private GitLab API token to use for \
                              authentication. Either this or username and \
                              password must be set.')
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
                             'output gets more verbose.',
                        default=0, action='count')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {0}'.format(__version__))
    args = parser.parse_args(argv)

    args.page_size = max(100, args.page_size)

    # Convert verbose flag to actually logging level
    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = log_levels[min(args.verbose, 2)]

    # Make warnings from built-in warnings module get formatted more nicely
    logging.captureWarnings(True)
    logging.basicConfig(format=('%(asctime)s - %(name)s - %(levelname)s - ' +
                                '%(message)s'), level=log_level)

    # Authenticate with GitLab instance using private token
    if args.token:
        gl = gitlab.Gitlab(args.gitlab_url, args.token)
    else:
        gl = None
    # make an API request to create the gl.user object. This is mandatory if you
    # use the username/password authentication.
    gl.auth()

    # Fetch all projects
    if args.verbose >= 2:
        print('Fetching all GitLab projects...', file=sys.stderr)
    projects = gl.projects.owned(all=True)
    # limited_projects = gl.projects.owned()

    if args.verbose >= 1:
        print('Processing GitLab projects...', file=sys.stderr)
    sys.stderr.flush()

    # Iterate over gitlab list of projects / repositories
    for project in projects:
        if args.verbose >= 2:
            print('\n' + ('=' * 80) + '\n', file=sys.stderr)
        sys.stderr.flush()

        # Project repository information
        proj_name = project.name
        tmp_path = "tmp/"
        tmp_proj_path = tmp_path + proj_name
        proj_description = project.description
        proj_repo_visibility = project.visibility_level
        proj_ssh_url_to_repo = project.ssh_url_to_repo

        if args.verbose >= 0:
            print("Processing: " + proj_name)

        # Clone repository in temporary directory
        if not os.path.exists(tmp_proj_path):
            if args.verbose >= 1:
                print("Cloning repository")

            if args.verbose >= 1:
                print(sh.pwd())

            sh.cd(tmp_path)
            sh.git.clone(proj_ssh_url_to_repo)

            if args.verbose >= 2:
                print("Clone completed")

            sh.cd("../")

        if args.verbose >= 1:
            print("Creating repository on BitBucket")

        sh.cd(tmp_proj_path)

        if args.verbose >= 1:
            print(sh.pwd())

        # Create bitbucket repository
        try:
            if proj_repo_visibility == "0":
                sh.git.bb("--private --description="+str(proj_description), 'create')
            else:
                sh.git.bb("--description="+str(proj_description), 'create')

            # Push content to bitbucket repository
            if args.verbose >= 1:
                print("Pushing repository")
                if args.verbose >= 2:
                    print(sh.pwd())
            sh.git.push("--all", "--repo", "bitbucket")

            if args.verbose >= 1:
                print("Pushing tags")
            sh.git("push", "--tags", "--repo", "bitbucket")
        except sh.ErrorReturnCode_1:
            if args.verbose >= 1:
                print('Failed. Repository already exists.', file=sys.stderr)

        if args.verbose >= 1:
            print(sh.pwd())

        sh.cd('../')

        # Disk Temporary Files Cleanup : Remove repository checkout
        sh.rm("--recursive", "--force", proj_name)

        sh.cd('../')
        if args.verbose >= 1:
            print(sh.pwd())
    if args.verbose >= 2:
        print('\n' + ('=' * 80) + '\n', file=sys.stderr)
    print("Import completed")

# execute program main
if __name__ == '__main__':
    main()

# fin
