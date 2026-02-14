# Zodiac Sign Bot 🌟

An automated system designed to streamline the process of fetching, generating, and posting daily horoscopes. This bot saves time by eliminating the manual work of copy-pasting text, designing images, and posting them to Instagram.

**Follow our daily updates on Instagram:** [Daily Horoscopes Astrology](https://www.instagram.com/daily_horoscopes_astrology?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==)

## 🚀 The Problem & Solution

**The Problem:**
Managing a daily horoscope page involves repetitive tasks:
1.  Visiting a website to copy horoscope text for all 12 signs.
2.  Pasting the text into an image editor.
3.  Designing a visually appealing layout.
4.  Exporting the images.
5.  Manually posting them to Instagram.

**The Solution:**
This bot automates the entire workflow!
-   **Scrapes** daily horoscope data automatically.
-   **Generates** aesthetic images using Python (Pillow) with custom fonts and templates.
-   **Sends** the generated images to a Telegram Bot for review.
-   **Auto-posts** to Instagram with a single click, including captions and hashtags.

## ✨ Features

-   **Automated Scraping**: Fetches accurate daily horoscope data for all zodiac signs.
-   **Dynamic Image Generation**: Uses `Pillow` to create high-quality, Instagram-ready images with custom fonts (Archivo Black, Glacial Indifference).
-   **Telegram Interface**: Control the bot via Telegram to select dates (Yesterday/Today/Tomorrow) and design templates.
-   **Instagram Integration**: Uses `instagrapi` to schedule or post directly to Instagram.
-   **Containerized**: Includes a `Dockerfile` for easy deployment.

## 🛠️ Tech Stack

-   **Python 3.10**
-   **Telegram Bot API** (`python-telegram-bot`)
-   **Image Processing**: `Pillow` (PIL)
-   **Web Scraping**: `requests`, `beautifulsoup4`
-   **Instagram API**: `instagrapi`
-   **Scheduling**: `APScheduler`
-   **Deployment**: Docker

## 📂 Project Structure

```
zodiac_sign_bot/
├── horoscope_bot/
│   ├── main.py            # Bot entry point and Telegram handlers
│   ├── scraper.py         # Logic to fetch horoscope text
│   ├── image_generator.py # Logic to create images from text
│   ├── instagram_manager.py # Handles Instagram login and posting
│   └── requirements.txt   # Python dependencies
├── Template-2/            # Assets for design template 2
├── final-template.../     # Assets for standard design template
├── Dockerfile             # Container configuration
└── ...fonts and assets
```

## 🚀 Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sameerreddy213/zodiac_sign_bot.git
    cd zodiac_sign_bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r horoscope_bot/requirements.txt
    ```

3.  **Environment Setup**:
    Create a `.env` file with your credentials:
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_token
    ```

4.  **Run the Bot**:
    ```bash
    python horoscope_bot/main.py
    ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.