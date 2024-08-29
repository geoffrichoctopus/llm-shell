# LLM-Shell

This is a command line tool written in Python designed to use Azure hosted AI endpoints to ask questions from the command line.

This can primarily be used to ask questions around shell commands on Linux.

Usage: main.py [-h] [--api_key API_KEY] [--endpoint_url ENDPOINT_URL] [--llm_type LLM_TYPE] [--query_type QUERY_TYPE] query

## Prerequisites

* Python 3
* rich pip package - `pip install rich`

## Installation

1. Clone this repo.
2. Install the rich pip package.
3. Set up an alias to run this to make it easy to run. Add an alias to your bashrc or zshrc file, ie `alias llm-shell='~/Repos/llm-shell/main.py'`

## How to use

The first time you run this tool, supply an `api_key`, an `endpoint_url` and the `llm_type`. The `api_key` and `endpoint_url` can be found on your Azure OpenAI resource. If you are connecting to a ChatGPT API, use "GPT" as the `llm_type`. If you are connecting to a llama llm (ie llama 3), use "llama" as the `llm_type`.

The endpoint_url, api_key and llm_type only needs to be supplied once as these details will be saved into a config.json in ~/.llm-shell and re-used.

If you ever need to change these details, re-supply them via the command line and the config.json will be updated.

## LLM Types

This script supports connecting to both ChatGPT and LLama3 endpoints. The following options are available:

* GPT
* llama

## Query Types

This defaults to "shell", the following options are available, along with the system prompt used for your query:

* shell: You are an assistant that helps people write shell commands for linux or mac.
* kubectl: You are an assistant that helps people write kubectl commands for interacting with Kubernetes.
* powershell : You are an assistant that helps people write powershell commands.

This can be set using the llm_type command line option.

## Examples

First use: `./main.py --api_key xxxxxxx --endpoint_url https://some.url --llm_type GPT "How to I unzip a .tar.gz file?"`

Subsequent uses: `./main.py "How to I unzip a .tar.gz file?"`

Kubectl query example: `./main.py --query_type kubectl "How to I scale a deployment?"`

## Output

The output is piped back into the termainal and formatted as per the markdown returned from the API endpoint.

## Notes

Ensure the query is surrounded by quotes.
