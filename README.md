gitlab-to-bitbucket
====================

A simple custom and basic solution to provide a command line tool which mirrors gitlab.com account repositories to bitbucket.org account repositories

This script depends heavily on existing tools and libraries to do most of the heavy lifting.

Note: This solution is stable and tested as functional.


Version
=======

* The current version of GitLab to BitBucket is 0.1.2

* Last Major update: March 24, 2017


Copyright
=========

* GitLab to BitBucket is copyright 1999 - 2017 Brookins Consulting

* See: [COPYRIGHT.md](COPYRIGHT.md) for more information on the terms of the copyright and license


License
=======

GitLab to BitBucket is licensed under the GNU General Public License.

The complete license agreement is included in the [LICENSE](LICENSE.md) file.

GitLab to BitBucket is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License or at your
option a later version.

GitLab to BitBucket is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

The GNU GPL gives you the right to use, modify and redistribute
GitLab to BitBucket under certain conditions. The GNU GPL license
is distributed with the software, see the file [LICENSE](LICENSE.md).

It is also available at [http://www.gnu.org/licenses/gpl.txt](http://www.gnu.org/licenses/gpl.txt)

You should have received a copy of the GNU General Public License
along with GitLab to BitBucket in in the [LICENSE](LICENSE.md) file.

If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).

Using GitLab to BitBucket under the terms of the GNU GPL is free (as in freedom).

For more information or questions please contact: license@brookinsconsulting.com


Requirements
============

The following requirements exists for using GitLab to BitBucket script:

- Python 3
- Python Library: sh
- Python Library: python-gitlab
- Python Library: git-spindle


# Required software

- GNU/Linux
- bash, 4.1.2(1)-release
- python, 3.x
- pip, ?rev
- git, 2.1.2
- coreutils, ?rev


## Install requirements

   pip install sh

   pip install python-gitlab

   pip install git-spindle


## Configure Requirements

## GitSpindle

GitSpindle provides for a configuration dot file ~/.gitspindle in INI file format.

You must create this file and populate it with the following. Customize it's contents to contain your actual BitBucket username and password.

This limited file format does not apear to support multiple accounts at the time of writting. We stored and manually uncommented our accounts + passwords as needed.

Please *remember* to switch this information or you may corrupt / cross polute your accounts when working with multiple accounts. This is a real bottle neck for users with multiple accounts at this time.

Note: Do not share this file with anyone. Ever. Lest the daemons haunt you.


### Example GitSpindle Configuration File Content

     [bitbucket]
            user = <bitbucket-username>
            password = <bitbucket-password>

## (Optional) SSH Host Aliases

If your like us we use this solution with multiple services, accounts, access tokens and ssh keys.

If your primary ssh key is not the right key you can fix this manually yourself *or* you can use the built in features of this script combined with ssh host aliases.

Here is an example of runing the command with expectations of use of ssh host aliases which follow the following convention (host(with no 1st level domain, .com))-as-(username of gitlab and bitbucket). This script assumes the usernames are the same between the two services.

    fucker

Here is an example of our (redacted) ssh configuration of ssh host aliases.

    Host github.com
    #Host github-as-bc
      HostName github.com
      User git
      IdentityFile /home/username/.ssh/id_rsa
      IdentitiesOnly yes

    Host github-as-ezpublishlegacy
      HostName github.com
      User git
      IdentityFile /home/username/.ssh-ezpl/id_rsa
      IdentitiesOnly yes

    Host github-as-ezpublishlegacyprojects
      HostName github.com
      User git
      IdentityFile /home/username/.ssh-ezplp/id_rsa
      IdentitiesOnly yes

    Host github-as-ezecosystem
      HostName github.com
      User git
      IdentityFile /home/username/.ssh-eze/id_rsa
      IdentitiesOnly yes


## Gitlab Access Requires

- GitLab Account, Personal Access Token
- BitBucket, Username and Password

## Note: Bitbucket repository urls are forced to be lower case only

Due to long standing limitations of the bitbucket.org platform all repository urls, repository names (slugs) (somereponame.git) must be lower case only.

This specifically affects a repository's directory name and git remote repository name


Usage
=====

## Direct python execution, Required Parameters Only (Within interactive shell only)

     ~/bin/gitlab-to-bitbucket/bin/gitlab_to_bitbucket.py --token=<github-personal-access-token-string>


## Direct python execution, Parameters required for most common use cases (Within interactive shell only)

     ~/bin/gitlab-to-bitbucket/bin/gitlab_to_bitbucket.py --token=<github-personal-access-token-string> --fetch-all --page-size=100

## Direct python execution, Parameters required for most common use cases using very verbose mode (Within interactive shell only)

     ~/bin/gitlab-to-bitbucket/bin/gitlab_to_bitbucket.py --token=<github-personal-access-token-string> --fetch-all --page-size=100 -vv

## Direct python execution, Parameters required for ssh host alias usage, second most common use cases using very verbose mode (Within interactive shell only)

     ~/bin/gitlab-to-bitbucket/bin/gitlab_to_bitbucket.py --token=<github-personal-access-token-string> --fetch-all --host-alias --page-size=100 -vv

## Direct python execution, Example usage with (most) script output logged to a temporary file

     ~/bin/gitlab-to-bitbucket/bin/gitlab_to_bitbucket.py --token=<github-personal-access-token-string> --fetch-all --host-alias --page-size=100 -vv 2> /home/username/gitlab-to-bitbucket-mirroring-test-run-0001.txt

*Note*: For longer runing usage (accounts with large numbers of project repositories and or large disk usage per repository) we *stronly* recommend only running our script within a GNU Screen Session (command: screen) which ensures the program (script) runs correctly in the event your ssh connection is interupted or terminated on accident.


# Related Documentation

- https://pypi.python.org/pypi/git-spindle

- http://seveas.github.io/git-spindle

- http://python-gitlab.readthedocs.io/en/stable/

- https://docs.gitlab.com/ee/api/README.html


Testing
=====

The solution is configured to work once properly installed and configured.


Troubleshooting
===============

### Read the FAQ

Some problems are more common than others. The most common ones are listed in the the [FAQ.md](FAQ.md)


### Support

If you have find any problems not handled by this document or the FAQ you can contact Brookins Consulting through the support system: [http://brookinsconsulting.com/contact](http://brookinsconsulting.com/contact)
