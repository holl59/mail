#!/bin/bash


if [ "$#" -lt 2 ]; then
    echo "usage $0 version release"
    exit 1
fi

ARCH=$(uname -m)
VERSION=$1
RELEASE=$2

SAM=sam-${VERSION}-${ARCH}.tar.gz
wget http://apps.syncloud.org/apps/${SAM} --progress=dot:giga
tar xzf $SAM -C /opt/app
/opt/app/sam/bin/sam update --release ${RELEASE}
/opt/app/sam/bin/sam --debug upgrade platform