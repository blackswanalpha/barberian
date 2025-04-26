#!/bin/bash

# Create a tar.gz archive of the Barberian project
# Excluding unnecessary files and directories

# Set the archive name
ARCHIVE_NAME="barberian_$(date +%Y%m%d).tar.gz"

# Create the archive
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

echo "Archive created: $ARCHIVE_NAME"
echo "Size: $(du -h $ARCHIVE_NAME | cut -f1)"
