# Real Estate Lead Triage System

A web application that processes, scores, and classifies real estate leads using rule-based scoring and AI-powered intent classification.

## 🎯 Features

- **Rule-based scoring**: 0-100 point system based on location, budget, timeframe, contact info, and message quality
- **AI Intent Classification**: Uses Groq LLM to classify lead intent (serious_buyer, serious_renter, seller, spam, etc.)
- **Tier System**: Automatically categorizes leads as Hot, Medium, Low, or Junk
- **Interactive Dashboard**: Search, filter, and view detailed lead information
- **Analytics**: Visual charts showing hot leads by source

## 📁 Project Structure

```
real-estate-triage/
├── backend/
│   ├── __init__.py
│   ├── app.py              # FastAPI application & routes
│   ├── constants.py        # Business logic constants (easy to tune)
│   ├── llm_client.py       # Groq API integration
│   ├── models.py           # Pydantic data models
│   └── scoring.py          # Lead scoring engine
├── frontend/
│   ├── templates/
│   │   └── index.html      # Dashboard UI
│   └── static/
│       ├── app.js          # Frontend logic
│       └── styles.css      # Custom styles
├── data/
│   └── test_leads_30.csv   # Sample leads data
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Groq API key (free tier available at https://console.groq.com)

### Installation

1. **Clone or extract the project**
   ```bash
   cd real-estate-triage
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your Groq API key:
   ```
   FREE_LLM_API_URL=https://api.groq.com/openai/v1/chat/completions
   FREE_LLM_API_KEY=your_actual_groq_api_key_here
   LEADS_CSV_PATH=data/test_leads_30.csv
   LOG_LEVEL=INFO
   PORT=8000
   ```

   **Get a free Groq API key:**
   1. Go to https://console.groq.com
   2. Sign up for a free account
   3. Navigate to API Keys section
   4. Create a new API key
   5. Copy and paste it into your `.env` file

### Running the Application

1. **Start the server**
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```

2. **Open your browser**
   ```
   http://127.0.0.1:8000
   ```

3. **Load and process leads**
   - Click the "Load & Process" button
   - The system will automatically load the CSV and process all leads
   - View results in the interactive table and charts

## 🎮 Usage

### Dashboard Features

1. **Search**: Type in the search box to filter leads by name, message, or source
2. **Filter by Tier**: Use the dropdown to show only Hot, Medium, Low, or Junk leads
3. **View Details**: Click "Open" on any lead to see full details including scoring reasons
4. **Analytics**: View hot leads distribution by source in the chart

### Custom CSV Path

To process a different CSV file, enter the path in the "Optional CSV path" field before clicking "Load & Process".

### Adjusting Business Logic

All scoring weights and thresholds are in `backend/constants.py`:
- `LOCATION_SCORES`: Points for different cities
- `BUDGET_SCORE_RULES`: Budget ranges and their scores
- `TIMEFRAME_SCORES`: Urgency scoring
- `TIERS`: Threshold for Hot/Medium/Low/Junk classification
- `SPAM_KEYWORDS`: Keywords that trigger spam detection

Simply edit these values and restart the server to see changes.

## 📊 Scoring System

Leads are scored on a 0-100 scale based on:

1. **Location** (0-25 points): Dubai and Abu Dhabi score highest
2. **Budget** (0-40 points): Higher budgets indicate serious intent
3. **Timeframe** (0-35 points): "now" scores highest, 6+ months lowest
4. **Contact Info** (0-27 points): Having both email and phone is best
5. **Message Quality** (varies): Keywords, length, spam detection
6. **Property Type Bonuses**: Sellers get +10, high-value properties get bonuses

### Tier Thresholds

- **Junk (0-39)**: Spam, incomplete, or irrelevant leads → Ignore
- **Low (40-64)**: Potential but needs nurturing → Nurture
- **Medium (65-79)**: Good leads → Call later
- **Hot (80-100)**: Excellent leads → Call now

## 🤖 AI Integration

The system uses Groq's LLM API to classify lead intent:

**Intent Labels:**
- `serious_buyer`: High purchase intent
- `serious_renter`: Genuine rental inquiry
- `seller`: Looking to sell property
- `casual_inquiry`: Browsing or exploring
- `spam`: Promotional or irrelevant content
- `not_relevant`: Not about real estate

**Current Model:** `llama-3.3-70b-versatile`

## 🛠️ Technical Stack

- **Backend**: FastAPI (Python web framework)
- **Frontend**: Vanilla JavaScript + Tailwind CSS
- **Templating**: Jinja2
- **Data Processing**: Pandas
- **Charts**: Chart.js
- **AI**: Groq API (Llama 3.3)
- **Storage**: In-memory (no database required)

## 📝 Design Decisions

1. **No Database**: In-memory storage for simplicity and fast demo
2. **Direct API Calls**: No agent frameworks - clean, transparent integration
3. **Modular Design**: Scoring, LLM, and constants separated for maintainability
4. **Error Handling**: Graceful fallbacks for LLM failures
5. **Tuneable Constants**: All business logic in one file for easy adjustment

## 🔧 Troubleshooting

### LLM API Errors
- Ensure your Groq API key is valid
- Check your internet connection
- System falls back to default classification if API fails

### CSV Loading Issues
- Ensure CSV has required columns: name, email, phone, property_type, budget, location_preference, timeframe_to_move, message, source
- Check file path in `.env` or provide custom path in UI

### Port Already in Use
```bash
# Use a different port
uvicorn backend.app:app --reload --port 8001
```

## 📈 Future Improvements

- Database integration (PostgreSQL/MongoDB)
- User authentication and multi-tenancy
- Email/SMS integration for lead follow-up
- More sophisticated ML models
- Lead assignment and workflow management
- Historical analytics and reporting
- Mobile app version

## 📄 License

This is a demo project for evaluation purposes.

## 👤 Author

Built as part of the Real Estate Lead Triage technical assessment.

---

**Need help?** Check the logs in the terminal for detailed error messages.