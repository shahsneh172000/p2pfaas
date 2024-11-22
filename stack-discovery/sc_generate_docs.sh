#!/usr/bin/env bash

function extract_module_name {
    # Extract module name
    sed -n -E 's/^\s*module\s+([[:graph:]]+)\s*$/\1/p'
}

function normalize_url {
    # Normalize provided URL. Removing double slashes
    echo "$1" | sed -E 's,([^:]/)/+,\1,g'
}

function generate_go_documentation {
    # Go doc
    local URL
    local PID
    local STATUS

    # Setup
    rm -rf "${GO_DOC_HTML_OUTPUT:-godoc}"

    # Extract Go module name from a Go module file
    if [[ -z "$GO_MODULE" ]]; then
        local FILE

        FILE="$(go env GOMOD)"

        if [[ -f "$FILE" ]]; then
            GO_MODULE=$(cat "$FILE" | extract_module_name)
        fi
    fi

    # URL path to Go package and module documentation
    URL=$(normalize_url "http://${GO_DOC_HTTP:-localhost:6061}/pkg/$GO_MODULE/")

    # Starting godoc server
    echo "Starting godoc server ${GO_DOC_HTTP:-localhost:6061}..."
    godoc -goroot=$(pwd) -http="${GO_DOC_HTTP:-localhost:6061}" &
    PID=$!

    echo "Final PID is $PID"


    echo "Waiting for godoc server to start at $URL"
    # Waiting for godoc server
    while ! curl --fail --silent "$URL" 2>&1 >/dev/null; do
        echo "Sleeping!"
        sleep 0.1
    done

    echo "Server started!"


    # Download all documentation content from running godoc server
    wget \
        --recursive \
        --no-verbose \
        --convert-links \
        --page-requisites \
        --adjust-extension \
        --execute=robots=off \
        --include-directories="/lib,/pkg/$GO_MODULE,/src/$GO_MODULE" \
        --exclude-directories="*" \
        --directory-prefix="${GO_DOC_HTML_OUTPUT:-godoc}" \
        --no-host-directories \
        "$URL" 
    # PID_WGET=$!

    # ps -aux

    # kill -s SIGKILL "$PID_WGET"

    echo "Downloaded docs..."

    # Stop godoc server
    kill -SIGKILL "$PID"
    echo "Stopped godoc server"
    echo "Go source code documentation generated under ${GO_DOC_HTML_OUTPUT:-godoc}"

    exit 0
}

generate_go_documentation