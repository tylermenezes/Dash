# Dash

Dash is a server which manages really simple deployments using Github. Dash receives push events from Github and uses
them to update your websites automatically.

Dash is very simple; it doesn't do much.

## Configuration

Have a look at the sample configuration file, `app/config.sample.json`. It contains a list of repositories Dash is
responsible for. Each repository contains a "secret" (which Github uses to sign requests), and a list of branches.

Each branch contains a "directory" - the location Dash should update when a commit is received - a "user" - the user
to update as (if any) - and, optionally, a list of post-update commands. (Note that the directory should already be
initialized and have the GitHub remote URL set as "origin".)