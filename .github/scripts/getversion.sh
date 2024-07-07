#!/bin/bash
Ver=$(cat version)
Version=$(echo $Ver | cut -f1 -d-)
VersionType=$(echo $Ver | cut -f2 -d-)

echo "VERSION=$Version" >> $GITHUB_ENV
echo "VERSIONTYPE=$VersionType" >> $GITHUB_ENV
