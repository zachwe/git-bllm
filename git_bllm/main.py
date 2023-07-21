import os
import subprocess
import click
import openai
from rich.live import Live
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
import os

console = Console()
openai_api_key = os.environ.get("OPENAI_API_KEY")

def explain_diff(diff):
    """Function to explain a git diff using the OpenAI API."""

    # Explain the diff
    global openai_api_key
    if openai_api_key is None:
        cache_dir = os.path.expanduser("~/.cache/git-bllm")
        if os.path.exists(cache_dir) and os.path.isfile(os.path.join(cache_dir, "openai_api_key")):
            with open(os.path.join(cache_dir, "openai_api_key")) as f:
                openai_api_key = f.read().strip()
        else:
            openai_api_key = Prompt.ask("Please enter your OpenAI API key")
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            with open(os.path.join(cache_dir, "openai_api_key"), "w") as f:
                f.write(openai_api_key)
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Please explain the following code diff: \n" + diff},
        ],
        stream=True
    )
    full_result = ""
    with Live(console=console, refresh_per_second=10) as live:
        for resp in response:
            delta = resp.choices[0].delta
            full_result += delta.get("content", "")
            md = Markdown(full_result)
            live.update(md)


def handle_commit_hash(commit_hash):
    """Function to handle when a commit hash is passed."""

    # Run 'git show' to get the diff
    result = subprocess.run(['git', 'show', commit_hash], stdout=subprocess.PIPE)
    diff = result.stdout.decode('utf-8')

    # Explain the diff
    explain_diff(diff)

def handle_file_path(file_path):
    """Function to handle when a file path is passed."""

    # TODO: implement this function

@click.command()
@click.argument('input', type=str)
def main(input):
    """Main function to handle the command line arguments."""

    # Check if the input is a file path
    if os.path.isfile(input):
        # If it's a file path, handle it as such
        handle_file_path(input)
    else:
        # If it's not a file path, check if it's a valid commit hash
        result = subprocess.run(['git', 'rev-parse', '-q', '--verify', input], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            # If it's a valid commit hash, handle it as such
            handle_commit_hash(input)
        else:
            print("Invalid input. Please provide either a valid file path or commit hash.")

if __name__ == "__main__":
    main()

