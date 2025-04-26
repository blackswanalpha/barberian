#!/bin/bash

# Create a tar.gz archive of the Barberian project with a manifest
# Excluding unnecessary files and directories

# Set the archive name and manifest name
DATE=$(date +%Y%m%d)
ARCHIVE_NAME="barberian_${DATE}.tar.gz"
MANIFEST_NAME="barberian_manifest_${DATE}.txt"

# Create a manifest of files to be included
echo "Creating manifest of files to be included in the archive..."
find . -type f \
    -not -path "./venv/*" \
    -not -path "./env/*" \
    -not -path "./.git/*" \
    -not -path "*/__pycache__/*" \
    -not -name "*.pyc" \
    -not -name "*.pyo" \
    -not -name "*.pyd" \
    -not -name "db.sqlite3" \
    -not -path "./media/*" \
    -not -path "./staticfiles/*" \
    -not -name ".env" \
    -not -path "./brber-master/*" \
    | sort > $MANIFEST_NAME

# Count the number of files
FILE_COUNT=$(wc -l < $MANIFEST_NAME)
echo "Found $FILE_COUNT files to include in the archive."

# Create the archive
echo "Creating archive $ARCHIVE_NAME..."
tar --exclude="venv" \
    --exclude="env" \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude="*.pyd" \
    --exclude="db.sqlite3" \
    --exclude="media/*" \
    --exclude="staticfiles" \
    --exclude=".env" \
    --exclude="brber-master" \
    -czvf $ARCHIVE_NAME .

# Add the manifest to the archive
tar -rf $ARCHIVE_NAME $MANIFEST_NAME

echo "Archive created: $ARCHIVE_NAME"
echo "Size: $(du -h $ARCHIVE_NAME | cut -f1)"
echo "Manifest created: $MANIFEST_NAME"
