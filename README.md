# LLM-Shell

This is a command line tool written in Python designed to use Azure hosted AI endpoints to ask questions from the command line.

This can primarily be used to ask questions around shell commands on Linux.

Usage: main.py [-h] [--api_key API_KEY] [--endpoint_url ENDPOINT_URL] [--llm_type LLM_TYPE] [--query_type QUERY_TYPE] query

## Prerequisites

* Python 3
* rich pip package - `pip install rich`

## How to use

The first time you run this tool, supply an `api_key` and an `endpoint_url` which can be found from your Azure resource. 

The endpoint_url and api_key only needs to be supplied once as these details will be saved into a config.json in ~/.llm-shell and re-used.

If you ever need to change these details, re-supply them via the command line and the config.json will be updated.

## LLM Types

This defaults to "shell-bash", the following options are available, along with the system prompt used for your query:

* shell-bash: You are an assistant that helps people write shell commands for linux for bash.
* kubectl: You are an assistant that helps people write kubectl commands for interacting with Kubernetes.
* powershell : You are an assistant that helps people write powershell commands.

This can be set using the llm_type command line option.

## Examples

First use: `./main.py --api_key xxxxxxx --endpoint_url https://some.url "How to I unzip a .tar.gz file?"`

Subsequent uses: `./main.py "How to I unzip a .tar.gz file?"`

Kubectl query example: `./main.py --query_type kubectl "How to I scale a deployment?"`

## Output

The output is piped back into the termainal and formatted as per the markdown returned from the API endpoint.

## Notes

Ensure the query is surrouned by quotes.
