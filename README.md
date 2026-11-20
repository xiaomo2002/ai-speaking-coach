# SpeakQuest · AI Speaking Coach

A friendly, gamified English speaking practice app. Play short daily speaking challenges, practice real-life phrases with browser speech recognition, and track XP and progress locally.

> English practice in your browser. No account, server, API key, or paid AI service required.

## Features

- Real-life conversation prompts and progressive learning levels
- Microphone speech recognition where supported; optional typing fallback
- Built-in text-to-speech for example phrases
- Word-level feedback, streaks, XP, and saved progress
- Responsive design for desktop and mobile

## Run

Open `index.html` in a modern browser, or host the repository with GitHub Pages. Microphone recognition works most reliably on HTTPS in Chrome or Edge. Safari and Firefox may vary; use typing fallback when unavailable.

## Privacy and limitations

Progress is stored in your browser via `localStorage` only. Voice recognition uses the browser-provided Web Speech API and may rely on your browser vendor's online speech service; do not assume microphone audio stays on your device. Scores compare recognized words with an expected phrase; they **do not** measure pronunciation quality as a dedicated speech assessment model would.

## License

MIT
