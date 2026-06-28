#!/bin/bash
set -e

BRANCH="gao"

# 如果本地没有该分支则创建
if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
  git checkout -b $BRANCH
else
  git checkout $BRANCH
fi

git add .
git commit -m "${1:-update}" 2>/dev/null || echo "nothing to commit"
git push -u origin $BRANCH

echo "pushed to origin/$BRANCH"
