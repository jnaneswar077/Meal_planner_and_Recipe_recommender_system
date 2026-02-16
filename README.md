# 🍽️ Smart Meal Planner

An AI-powered meal planning application with recipe recommendations, weekly meal planning, and automatic shopping list generation.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)

## ✨ Features

- **🔍 Smart Recipe Search** - Natural language search across 222K+ recipes using TF-IDF & Cosine Similarity
- **📅 Meal Planning** - Weekly calendar with breakfast, lunch, and dinner slots
- **🛒 Shopping Lists** - Auto-generated from meal plans with ingredient consolidation
- **🔐 User Authentication** - Secure JWT-based login system
- **🌙 Dark Mode** - Modern UI with light/dark theme toggle

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Vite, React Router |
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **ML** | scikit-learn (TF-IDF, Cosine Similarity) |
| **Auth** | JWT, bcrypt |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Recipe dataset CSV file

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-meal-planner.git
cd smart-meal-planner

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### Configuration

Update the recipe data path in `backend/config.py`:
```python
RECIPES_CSV_PATH = "path/to/your/cleaned_recipes.csv"
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## 📁 Project Structure

```
smart-meal-planner/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── config.py            # Configuration
│   ├── routes/              # API endpoints
│   │   ├── auth.py         
│   │   ├── recipes.py      
│   │   ├── meal_plans.py   
│   │   └── shopping.py     
│   ├── services/
│   │   └── recommendation_engine.py
│   └── utils/
│       └── auth.py          # JWT utilities
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app + routing
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   └── services/api.js  # API client
│   └── index.html
│
└── explore/                  # Data exploration scripts
```

## 🔑 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/recipes/recommend` | Get recipe recommendations |
| GET | `/api/recipes/{id}` | Get recipe details |
| POST | `/api/meal-plans/create` | Create meal plan |
| POST | `/api/meal-plans/{id}/add-meal` | Add meal to plan |
| POST | `/api/shopping-lists/generate` | Generate shopping list |

## 📸 Screenshots

*Coming soon*

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built as a Final Year Project

---

⭐ Star this repo if you found it helpful!
