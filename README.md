# TARS - Tactical AI Response System

TARS is a CLI-based AI assistant inspired by the iconic tactical robot from *Interstellar*. Powered by Google Gemini, TARS is designed to provide dynamic, intelligent responses while maintaining its signature "military-grade" personality.

## 🤖 Features

- **Iconic Personality**: Pre-configured with 90% Honesty, 75% Humor, and a healthy dose of military-grade sarcasm.
- **Powered by Google Gemini**: Utilizes the latest Gemini 3.5 Flash model for fast and intelligent processing.
- **Enhanced CLI Experience**: Color-coded terminal output (Green for Users, Blue for TARS) for better readability.
- **Session History**: Maintains conversation context during active sessions.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- A Google AI Studio API Key ([Get one here](https://aistudio.google.com/))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/GNU-LuxTech/Tars.git
   cd Tars
   ```

2. **Set up the virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate # On Unix/macOS
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   Create a `.env` file in the root directory and add your API key:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## 🎮 Usage

Run the main script to start interacting with TARS:

```bash
python tars.py
```

- Type your message and press **Enter**.
- Type `exit` or `quit` to power down the system.

## ⚙️ Tactical Settings

Current TARS configuration:
- **Honesty**: 90%
- **Humor**: 75%
- **Sarcasm**: Standard Military-Grade

---
*"Plenty of slaves for my robot colony."* — TARS
