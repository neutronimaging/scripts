#!/bin/bash

# List all branches
branches=$(git for-each-ref --format='%(refname:short)' refs/heads/)

# Function to get the branch creation date
get_creation_date() {
    local branch=$1
    # Find the commit where the branch diverged from its parent branch
    local diverging_commit=$(git merge-base $branch $(git for-each-ref --format='%(refname:short)' refs/heads/ | grep -v $branch | head -n 1))
    # Get the commit date
    local creation_date=$(git show -s --format=%ci $diverging_commit)
    echo "$creation_date - $branch "
}

echo "Branch Name - Creation Date"
for branch in $branches
do
    get_creation_date $branch
done
