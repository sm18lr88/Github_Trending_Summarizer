import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time
import sys
import markdown
from rich.console import Console
from rich.markdown import Markdown
from pathlib import Path
import webbrowser


def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print(
            "OpenAI API key not found in environment variables. Please enter your OpenAI API key:"
        )
        api_key = input().strip()
        os.environ["OPENAI_API_KEY"] = (
            api_key  # Set it in the environment variables for future use
        )

    return api_key


def get_trending_repositories():
    url = "https://github.com/trending"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    repositories = soup.select("article.Box-row")

    repo_list = []
    for repo in repositories:
        repo_url = (
            f"https://github.com{repo.select_one('h2.h3.lh-condensed > a')['href']}"
        )
        repo_info = {
            "url": repo_url,
            "readme_url": repo_url.replace("github.com", "raw.githubusercontent.com")
            + "/HEAD/README.md",
            "language": (
                repo.select_one('span[itemprop="programmingLanguage"]').text.strip()
                if repo.select_one('span[itemprop="programmingLanguage"]')
                else "Not specified"
            ),
            "stars": repo.select_one('a[href*="/stargazers"]').text.strip(),
        }
        repo_list.append(repo_info)

    return repo_list


def save_data_to_markdown(repositories):
    timestamp = int(time.time())
    filename = f"trending_repos_{timestamp}.md"

    markdown_content = "# Trending GitHub Repositories\n\n"

    for repo in repositories:
        markdown_content += f"## {repo['url']}\n"
        markdown_content += f"**Description:** [README URL]({repo['readme_url']})\n"
        markdown_content += f"**Primary Language:** {repo['language']}\n"
        markdown_content += f"**Stars:** {repo['stars']}\n"
        markdown_content += "\n---\n\n"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(markdown_content)

    return filename


def get_processed_info_from_gpt(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = file.read()

    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)

    example_response = """
## [coqui-ai/TTS](https://www.github.com/coqui-ai/tts)
**Description:** A deep learning toolkit for Text-to-Speech with pretrained models in +1100 languages, battle-tested in research and production. Utilizes models like Tacotron, Glow-TTS, and VITS to convert text into spectrograms, which are then transformed into audio using vocoder models like MelGAN and WaveRNN. Supports training and fine-tuning models, enabling multi-speaker TTS and voice cloning. Use cases include virtual assistants, accessibility tools, and custom voice applications.

- **Primary Language:** Python

- **Stars:** 31k

- **Operating Systems:** Ubuntu mainly; Windows instructions available

- **Needs Compilation?** No: script provided automates install

- **Self-hosting:** local and online

    """

    system_message = (
        "You are a helpful assistant that provides thorough summaries of GitHub repositories based on their README.md files. "
        "In these summaries, include a brief description that explains both what the repository does and how it functions. "
        "When describing the 'framework,' explain the core components, architecture, and workflow of how the program operates—not just the libraries or tools it uses. "
        "For example, if a TTS program converts text to speech, detail how it processes text, generates spectrograms, and produces audio. "
        "Include practical use cases based on the README.md. "
        "Pay special attention to the `Needs Compilation?` section so that your answer **EXPLAINS** based on the README.md., rather than only saying `yes` or `no. "
        "Also pay attention to the new lines in between each sub-item in order to properly render each in a new line. "
        "Format each repository summary as follows:\n "
        f"{example_response}\n"
        "Here is the list of repositories:\n "
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": data},
        ],
        max_tokens=4000,
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_markdown_to_html(markdown_filename):
    with open(markdown_filename, "r", encoding="utf-8") as file:
        markdown_content = file.read()

    html_content = markdown.markdown(markdown_content)

    css_path = "custom.css"
    if not os.path.exists(css_path):
        css_content = """
        /* Sepia Theme for HTML Rendering */
        body {
            background-color: #f4ecd8;
            font-family: "Merriweather", Georgia, serif;
            line-height: 1.6;
            margin: 0 auto;
            max-width: 800px;
            padding: 20px;
            color: #5b4636;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: "Merriweather", Georgia, serif;
            color: #5b4636;
            margin-top: 1.4em;
            margin-bottom: 0.6em;
        }
        p {
            margin-top: 0.6em;
            margin-bottom: 0.6em;
        }
        code, pre {
            background-color: #f3eac7;
            border-radius: 3px;
            padding: 2px 4px;
        }
        blockquote {
            border-left: 4px solid #d0c4af;
            color: #5b4636;
            padding-left: 10px;
            margin-left: 0;
            margin-right: 0;
            font-style: italic;
        }
        ul, ol {
            padding-left: 40px;
        }
        hr {
            border: 1px solid #d0c4af;
        }
        .container {
            background-color: #fffaf0;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        """
        with open(css_path, "w", encoding="utf-8") as css_file:
            css_file.write(css_content)

    html_output = f"""
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="{css_path}">
    </head>
    <body>
        <div class="container">
            {html_content}
        </div>
    </body>
    </html>
    """

    html_filename = markdown_filename.replace(".md", ".html")
    with open(html_filename, "w", encoding="utf-8") as file:
        file.write(html_output)

    return html_filename


def display_in_terminal(processed_info):
    console = Console()
    console.print(Markdown("# Processed GitHub Repositories\n"))

    repos = processed_info.split("\n---\n")
    for repo in repos:
        repo_md = Markdown(repo.strip())
        console.print(repo_md)
        console.print("\n" + "-" * 80 + "\n")


def main():
    api_key = get_openai_api_key()
    repo_list = get_trending_repositories()
    markdown_file = save_data_to_markdown(repo_list)
    processed_info = get_processed_info_from_gpt(markdown_file)

    timestamp = int(time.time())
    output_filename = f"processed_repos_{timestamp}.md"

    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(processed_info)

    file_path = Path(output_filename).resolve()
    folder_path = file_path.parent
    console = Console()
    console.print(
        f"Processed information saved to [bold green]{output_filename}[/bold green]. Open the folder containing the file: [link=file://{folder_path}]{folder_path}[/link]",
        style="bold blue",
    )

    while True:
        print(
            "\nFile processed successfully! You can render the file as HTML or display it in the terminal."
        )
        print("1. Render as HTML and open in browser")
        print("2. Display in terminal")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            html_filename = render_markdown_to_html(output_filename)
            os.startfile(html_filename)
            break
        elif choice == "2":
            display_in_terminal(processed_info)
            break
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

    while True:
        print("\nWhat would you like to do now?")
        print("1. Delete the created file.")
        print("2. Render as HTML and open in browser.")
        print("3. Display in terminal.")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            os.remove(output_filename)
            print(f"{output_filename} has been deleted.")
            html_filename = output_filename.replace(".md", ".html")
            if os.path.exists(html_filename):
                os.remove(html_filename)
            print(f"Files have been deleted.")
            break
        elif choice == "2":
            html_filename = render_markdown_to_html(output_filename)
            os.startfile(html_filename)
        elif choice == "3":
            display_in_terminal(processed_info)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Please try again.")

    sys.exit()


if __name__ == "__main__":
    main()
