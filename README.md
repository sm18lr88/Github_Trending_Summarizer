# Github_Trending_Summarizer

Fetch and summarize key data -> render in markdown in the terminal or browser. See pictures below.

## Features

- Fetch trending GitHub repositories
- Summarize repository details using GPT-4o
- Display summaries in the terminal with rich formatting (with clickable links!).
- Render summaries as HTML with a nice Sepia theme.

## Requirements

- Python 3.9 or higher
- Required Python packages (see `requirements.txt`)
- OpenAI [API key](https://platform.openai.com/login?launch)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/sm18lr88/Github_Trending_Summarizer.git
    cd Github_Trending_Summarizer
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```bash
python gh_trending.py
```

Follow the prompts to fetch trending repositories and choose how to view the summaries:
- Render as HTML and open in browser
- Display in terminal

You can also choose to delete the created files after viewing them.

## Examples
---
<image src='https://github.com/sm18lr88/Github_Trending_Summarizer/assets/64564447/7ac60372-9453-4f39-80f3-814520f6959f' width='800'>
    
---

<image src='https://github.com/sm18lr88/Github_Trending_Summarizer/assets/64564447/302895ae-7ef0-48e3-930a-620a56c2788e' width='800'>
    
---

<image src='https://github.com/sm18lr88/Github_Trending_Summarizer/assets/64564447/f6c07204-950d-47e7-bcf4-cdd38b0c58e2' width='800'>


## License

This project is licensed under a custom license for personal use only. See the [LICENSE](LICENSE) file for details.
