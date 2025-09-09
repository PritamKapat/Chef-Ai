# TODO List for Groq API Key Setup

- [x] Create .env file in project root with GROQ_API_KEY placeholder
- [x] Update projectname/projectname/settings.py to load environment variables from .env
- [x] Update projectname/Airecipe/views.py to use os.getenv('GROQ_API_KEY') instead of empty string
- [x] Install python-dotenv (if not already installed)

## Followup Steps
- [ ] Replace 'your_groq_api_key_here' in .env with your actual Groq API key
- [ ] Test the application to ensure the API key is loaded correctly
