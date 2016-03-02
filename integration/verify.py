import os
import sys
from os import listdir
from os.path import dirname, join, abspath, isdir
import time
from subprocess import check_output

import pytest
import re

app_path = join(dirname(__file__), '..')
sys.path.append(join(app_path, 'src'))

lib_path = join(app_path, 'lib')
libs = [abspath(join(lib_path, item)) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda x: sys.path.insert(0, x), libs)

import requests
import shutil

from integration.util.ssh import run_scp, ssh_command, SSH, run_ssh, set_docker_ssh_port

DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')
SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
DEFAULT_DEVICE_PASSWORD = 'syncloud'


@pytest.fixture(scope='module')
def user_domain(auth):
    email, password, domain, release, version, arch = auth
    return 'mail.{0}.{1}'.format(domain, SYNCLOUD_INFO)


@pytest.fixture(scope='function')
def syncloud_session():
    session = requests.session()
    session.post('http://localhost/server/rest/login', data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    return session


def test_remove_logs():
    shutil.rmtree(LOG_DIR, ignore_errors=True)


def test_activate_device(auth):
    email, password, domain, release, version, arch = auth

    run_ssh('/opt/app/sam/bin/sam update --release {0}'.format(release), password=DEFAULT_DEVICE_PASSWORD)
    run_ssh('/opt/app/sam/bin/sam --debug upgrade platform', password=DEFAULT_DEVICE_PASSWORD)

    response = requests.post('http://localhost:81/server/rest/activate',
                             data={'main_domain': 'syncloud.info', 'redirect_email': email, 'redirect_password': password,
                                   'user_domain': domain, 'device_username': DEVICE_USER, 'device_password': DEVICE_PASSWORD})
    assert response.status_code == 200


def test_install(auth):
    __local_install(auth)


def test_running_smtp():
    print(check_output('nc -zv -w 1 localhost 25', shell=True))


def test_running_pop3():
    print(check_output('nc -zv -w 1 localhost 110', shell=True))


def test_running_roundcube():
    print(check_output('nc -zv -w 1 localhost 1100', shell=True))


# def test_upload_profile_photo(diaspora_session, user_domain):
#
#     response = diaspora_session.get('https://127.0.0.1/profile/edit',
#                                     headers={"Host": user_domain},
#                                     allow_redirects=False, verify=False)
#     assert response.status_code == 200, response.text
#
#     soup = BeautifulSoup(response.text, "html.parser")
#     token = soup.find_all('meta', {'name': 'csrf-token'})[0]['content']
#
#     response = diaspora_session.post('https://127.0.0.1/photos',
#                                      headers={
#                                          "Host": user_domain,
#                                          'X-File-Name': 'profile.png',
#                                          'X-CSRF-Token': token
#                                      },
#                                      verify=False, allow_redirects=False,
#                                      params={
#                                          'photo[pending]': 'true',
#                                          'photo[aspect_ids]': 'all',
#                                          'photo[set_profile_photo]': 'true',
#                                          'qqfile': 'profile.png'
#                                      })
#     assert response.status_code == 200, response.text

    # with open(join(DIR, 'images', 'profile.png'),'rb') as payload:
    #     headers = {'content-type': 'application/x-www-form-urlencoded'}
    #     r = requests.post('https://IP_ADDRESS/rest/rest/2', auth=('userid', 'password'),
    #                   data=payload, verify=False, headers=headers)

# def test_authenticated_resource(diaspora_session):
#     response = diaspora_session.get('http://localhost/diaspora/', allow_redirects=False)
#     soup = BeautifulSoup(response.text, "html.parser")
#     requesttoken = soup.find_all('input', {'name': 'requesttoken'})[0]['value']
#     response = diaspora_session.post('http://localhost/diaspora/index.php',
#                             data={'user': device_user, 'password': device_password, 'requesttoken': requesttoken},
#                             allow_redirects=False)
#
#     assert response.status_code == 302, response.text
#
#     assert session.get('http://localhost/diaspora/core/img/filetypes/text.png').status_code == 200

# def test_admin():
#     response = session.get('http://localhost/diaspora/index.php/settings/admin', allow_redirects=False)
#     assert response.status_code == 200, response.text

# def test_remove():
#     session.post('http://localhost/server/rest/login', data={'name': device_user, 'password': device_password})
#     response = session.get('http://localhost/server/rest/remove?app_id=diaspora', allow_redirects=False)
#     assert response.status_code == 200, response.text


# def test_reinstall(auth):
#     __local_install(auth)


def test_copy_logs():
    os.mkdir(LOG_DIR)
    run_scp('root@localhost:/opt/data/platform/log/* {0}'.format(LOG_DIR), password=DEVICE_PASSWORD)

    run_ssh('ls -la /opt/data/mail/log', password=DEVICE_PASSWORD)
    run_scp('root@localhost:/opt/data/mail/log/* {0}'.format(LOG_DIR), password=DEVICE_PASSWORD)

    print('-------------------------------------------------------')
    print('syncloud docker image is running')
    print('connect using: {0}'.format(ssh_command(DEVICE_PASSWORD, SSH)))
    print('-------------------------------------------------------')


def __local_install(auth):
    email, password, domain, release, version, arch = auth
    run_scp('{0}/../mail-{1}-{2}.tar.gz root@localhost:/'.format(DIR, version, arch), password=DEVICE_PASSWORD)
    run_ssh('/opt/app/sam/bin/sam --debug install /mail-{0}-{1}.tar.gz'.format(version, arch), password=DEVICE_PASSWORD)
    time.sleep(3)
