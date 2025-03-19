# ai-writing-assistant - Writing Assistant with OpenAI

ai-writing-assistant is an AI-powered writing assistant application that helps users improve their writing through AI feedback, writing prompts, and interactive chat assistance.

## Features

### AI Assistant
- Interactive chat interface with OpenAI's powerful language models
- Support for multiple GPT models including GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, and O1 models
- Customizable AI responses with adjustable parameters (temperature, max tokens, etc.)
- Persistent chat history that saves your conversations

### Writing Prompts
- Organized writing prompts by categories
- Random prompt selection within categories
- Support for both text (.txt) and markdown (.md) files
- Easy integration of prompts into your writing workflow

### AI Feedback
- Get detailed AI feedback on your writing
- Customize feedback criteria
- Incorporate writing prompts into the feedback process
- Powered by OpenAI's language models for insightful analysis

## Getting Started

### Prerequisites
- Python 3.6+
- PyQt6
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-writing-assistant.git
cd ai-writing-assistant
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
python main.py
```

## Configuration

### OpenAI API Key
To use the AI features, you'll need to set up your OpenAI API key in the application settings.

### Writing Prompts
Create a folder structure for your writing prompts:
- Main folder (select this in the app)
  - Category1 (subfolder)
    - prompt1.md
    - prompt2.txt
  - Category2 (subfolder)
    - prompt3.md
    - prompt4.txt

## Usage

### AI Assistant
1. Navigate to the "AI Assistant" tab
2. Type your message in the input field
3. Press "Send" or hit Enter
4. View the AI's response in the chat display

### Writing Prompts
1. Navigate to the "Writing Prompts" tab
2. Select a prompts folder containing categorized prompts
3. Choose a category from the dropdown
4. Click "Get New Prompt" to display a random prompt
5. Use "Use Selected Prompt" to incorporate it into your writing

### AI Feedback
1. Enter your writing in the main editor
2. Optionally select a writing prompt
3. Specify feedback criteria
4. Request AI feedback
5. Review the detailed analysis and suggestions

## Technical Details

The application is built with:
- Python and PyQt6 for the user interface
- OpenAI API for AI capabilities
- Markdown rendering for rich text display
- JSON-based settings storage

## License

[Your License Information]

## Acknowledgments

- OpenAI for providing the API
- Contributors and testers
```

