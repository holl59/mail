#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

export TMPDIR=/tmp
export TMP=/tmp

NAME=mail
ROUNDCUBE_VERSION=1.3.1
ARCH=$(uname -m)
VERSION=$1

if [ -n "$DRONE" ]; then
    echo "running under drone, removing coin cache"
    rm -rf ${DIR}/.coin.cache
fi

rm -rf lib
mkdir lib

coin --to lib py https://pypi.python.org/packages/2.7/r/requests/requests-2.7.0-py2.py3-none-any.whl
coin --to lib py https://pypi.python.org/packages/source/s/syncloud-lib/syncloud-lib-2.tar.gz
coin --to lib py https://pypi.python.org/packages/source/t/tzlocal/tzlocal-1.2.2.tar.gz
coin --to lib py https://pypi.python.org/packages/source/p/pytz/pytz-2016.1.tar.gz

cp -r ${DIR}/src lib/syncloud-mail-${VERSION}

rm -rf build
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p ${BUILD_DIR}

DOWNLOAD_URL=http://artifact.syncloud.org/3rdparty

coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/postfix-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/dovecot-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/rsyslog-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/php7-${ARCH}.tar.gz
mv ${BUILD_DIR}/php7 ${BUILD_DIR}/php
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/nginx-${ARCH}.tar.gz
coin --to ${BUILD_DIR} raw ${DOWNLOAD_URL}/postgresql-${ARCH}.tar.gz

coin --to ${BUILD_DIR} raw https://github.com/roundcube/roundcubemail/releases/download/${ROUNDCUBE_VERSION}/roundcubemail-${ROUNDCUBE_VERSION}-complete.tar.gz

mv ${BUILD_DIR}/roundcubemail-${ROUNDCUBE_VERSION} ${BUILD_DIR}/roundcubemail

#https://github.com/roundcube/roundcubemail/issues/5949
rm ${BUILD_DIR}/roundcubemail/vendor/pear/net_smtp/README.rst

cp -r ${DIR}/bin ${BUILD_DIR}
cp -r ${DIR}/config ${BUILD_DIR}/config.templates
cp -r ${BUILD_DIR}/postfix/opt/data/mail/config/postfix/postfix-files ${BUILD_DIR}/config.templates/postfix
cp -r ${DIR}/lib ${BUILD_DIR}

mkdir build/${NAME}/META
echo ${NAME} > build/${NAME}/META/app
echo ${VERSION} > build/${NAME}/META/version

echo "zipping"
tar cpzf ${DIR}/${NAME}-${VERSION}-${ARCH}.tar.gz -C ${DIR}/build/ ${NAME}
