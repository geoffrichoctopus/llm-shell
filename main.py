#!/usr/bin/env python3

import urllib.request
import json
import os
import ssl
import argparse
import time
from rich.console import Console
from rich.markdown import Markdown

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

system_roles = {
    "shell-bash":"You are an assistant that helps people write shell commands for linux for bash.",
    "kubectl":"You are an assistant that helps people write kubectl commands for interacting with Kubernetes.",
    "powershell":"You are an assistant that helps people write powershell commands."
}
home_dir = os.path.expanduser("~")
app_dir = os.path.join(home_dir, ".llm-shell")
config_filename = os.path.join(app_dir, "config.json")

def is_env_var_true(var_name):
    return os.getenv(var_name, 'false').lower() == 'true'

def createRequestBodyLlama(system_role_content, user_content) -> str:
    return str.encode(json.dumps({
        "messages": [
            {
                "role": "system",
                "content": system_role_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        "max_tokens": 800,
        "temperature": 1,
        "top_p": 0.1,
        "best_of": 1,
        "presence_penalty": 0,
        "use_beam_search": "false",
        "ignore_eos": "false",
        "skip_special_tokens": "false",
        "stream": "false"
    }))

def createRequestBodyGPT(system_role_content, user_content) -> str:
    return str.encode(json.dumps({
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_role_content
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_content
                    }
                ]
            }
        ],
        "max_tokens": 800,
        "temperature": 1,
        "top_p": 0.1
    }))

def set_config_api_key(api_key):
    if os.path.exists(config_filename):
        config = json.loads(open(config_filename).read())
    else:
        config = {}
    config["api_key"] = api_key
    with open(config_filename, 'w') as f:
        f.write(json.dumps(config))

def set_config_endpoint_url(endpoint_url):
    if os.path.exists(config_filename):
        config = json.loads(open(config_filename).read())
    else:
        config = {}
    config["endpoint_url"] = endpoint_url
    with open(config_filename, 'w') as f:
        f.write(json.dumps(config))

def set_config_llm_type(llm_type):
    if os.path.exists(config_filename):
        config = json.loads(open(config_filename).read())
    else:
        config = {}
    config["llm_type"] = llm_type
    with open(config_filename, 'w') as f:
        f.write(json.dumps(config))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, help="The API key for the OpenAI endpoint")
    parser.add_argument("--endpoint_url", type=str, help="The URL for the OpenAI endpoint")
    parser.add_argument("--llm_type", type=str, help="The type of LLM to use, either llama or GPT")
    parser.add_argument("--query_type", type=str, help="Can be set to shell-bash or kubectl, defaults to shell-bash if not passed in.")
    parser.add_argument("query", type=str, help="The query to send to the OpenAI endpoint")
    args = parser.parse_args()
    #display a helpful message about how to use this tool if there are no arguments passed in
    if not any(vars(args).values()):
        print("Please provide an API key and an endpoint URL the first time you run this. All command line arguments are optional.")
        print("Example: python main.py --api_key <API_KEY> --endpoint_url <ENDPOINT_URL> --llm_type GPT --query-type kubectl \"query\"")
        print("Once provided, the api_key and endpoint_url will be saved in a config.json file for future use.")
        print("If the query-type parameter is not provided, it defaults to shell-bash.")
        print("This config file is saved into ~/.llm-shell/config.json")
        exit()
    return args

if __name__ == "__main__":
    args = parse_arguments()

    # Create config path if it doesnt exist
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    if args.api_key:
        set_config_api_key(args.api_key)
    if args.endpoint_url:
        set_config_endpoint_url(args.endpoint_url)
    if args.llm_type:
        set_config_llm_type(args.llm_type)

    #quit and error if config.json doesnt exist
    if not os.path.exists(config_filename):
        raise Exception("A config.json file should set with command line options for this script to run.")
    #load config.json into some variables
    config = json.loads(open(config_filename).read())

    if not config["api_key"]:
        raise Exception("An API key should be provided to invoke the endpoint. This can be passed in as a command line argument then saved in the config.json file.")
    if not config["endpoint_url"]:
        raise Exception("An endpoint url should be provided to invoke the endpoint. This can be passed in as a command line argument then saved in the config.json file.")
    if not config["llm_type"]:
        raise Exception("An LLM type should be provided to invoke the endpoint. This can be passed in as a command line argument then saved in the config.json file.")

    user_query = args.query
    system_role_type = "shell-bash"
    if args.query_type:
        system_role_type = args.query_type
    if system_roles.get(system_role_type) is None:
        raise Exception("The query type should be set to shell-bash or kubectl.")

    if config["llm_type"] == "llama":
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ config["api_key"])}
        requestBody = createRequestBodyLlama(system_roles[system_role_type], user_query)
    elif config["llm_type"] == "GPT":
        headers = { "Content-Type": "application/json",   "api-key": config["api_key"] }
        requestBody = createRequestBodyGPT(system_roles[system_role_type], user_query)
        
    req = urllib.request.Request(config["endpoint_url"], requestBody, headers, method='POST')
    try:
        start_time = time.time()
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        end_time = time.time()
        elapsed_time = end_time - start_time
        if is_env_var_true('LOG_EXECUTION_TIME'):
            print(f"Execution time: {elapsed_time:.4f} seconds")
        console = Console()
        markdown_text = result["choices"][0]["message"]["content"]
        md = Markdown(markdown_text)
        console.print(md)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

