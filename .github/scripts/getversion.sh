#!/bin/bash
Ver=$(cat version)
Version=$(echo $Ver | cut -f1 -d-)
VersionType=$(echo $Ver | cut -f2 -d-)

echo "Version=$Version" >> $GITHUB_ENV
echo "VersionType=$VersionType" >> $GITHUB_ENV
