# Tiny Top Games

A collection of simple games for my son, designed to run on an old 32-bit Acer KAV60 laptop. Built using cursor and other AI tools. 

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

If you want to use voice features, you'll need to set up an ElevenLabs API key:

1. Copy the sample environment file:
   ```bash
   cp env.example .env
   ```

2. Get your API key from [ElevenLabs](https://elevenlabs.io/)

3. Edit the `.env` file and replace `your_elevenlabs_api_key_here` with your actual API key:
   ```
   ELEVENLABS_API_KEY=sk-your-actual-api-key-here
   ```

## Run the game

```bash
python main_menu.py
```

## Notes

- Fixed window size: 1024x600 (native KAV60 res)


## TODO

* Add more kid-friendly games
