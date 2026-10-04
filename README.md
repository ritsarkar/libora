# Libora — Smart Library Management System

An Apple Human Interface Guidelines-inspired, modern library management web application engineered with Python Flask and SQLite. Libora provides real-time circulation tracking, catalog search, book issuing, late fee calculations, and automated receipt generation in an intuitive, translucent glassmorphism interface.

---

## ✨ Features

- **🍎 Apple HIG-Inspired Interface**: Clean typography, frosted glass materials (`backdrop-filter`), smooth spring transitions, and native SF Pro iconography without third-party icon fonts.
- **🔍 Optic Command Palette (`Ctrl+K` / `⌘+K`)**: Global Spotlight-style search modal to instantly look up books by Title, Author, Category, ISBN, or Rack location.
- **📚 Catalog & Inventory Tracking**: Real-time availability badges, rack location markers, and inventory statistics.
- **⚡ Book Circulation Workflow**:
  - **Issue Books**: Seamless checkout process linking student name, contact info, issue date, and due date.
  - **Return & Fine Calculation**: Automated overdue detection and late fee calculation.
  - **Digital Receipts**: Clean, printable billing receipts with reference numbers and date stamps.
- **🛡️ Dedicated Admin Management**: Add new books, assign rack locations, categorize inventory, and manage catalog data exclusively from the Admin Portal.
- **🎯 Context-Aware Navigation**: Adaptive navigation bar that intelligently hides redundant routes based on the current page.
- **📦 Zero-Config Persistence**: Built-in SQLite database with automated table migration and initial catalog seeding on first boot.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask
- **Database**: SQLite3
- **Frontend**: HTML5, Modern CSS3 (CSS Variables, Flexbox, CSS Grid, Glassmorphism), Vanilla JavaScript
- **Icons**: Custom Apple SF Symbols SVG glyphs

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/ritsarkar/libora.git
cd libora
```

### 2. Create and activate a virtual environment (optional but recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## ☁️ Deploy to Vercel

Libora supports native zero-configuration deployment on [Vercel](https://vercel.com):

1. **Push your repository to GitHub** (already done: `https://github.com/ritsarkar/libora`).
2. Go to your [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New..." > "Project"**.
3. Import your **`libora`** repository.
4. Leave all settings at their defaults (Framework: **Flask / Other**, Root Directory: `./`).
5. Click **"Deploy"**.

> [!NOTE]
> Vercel automatically detects the Flask application via `app.py` and `requirements.txt`. The SQLite database is safely initialized in `/tmp/library.db`, preventing serverless read-only filesystem errors.

---

## 📁 Project Structure

```
├── app.py                      # Core Flask application, routing, and SQLite models
├── wsgi.py                     # WSGI entry point
├── requirements.txt            # Python dependencies (Flask)
├── .gitignore                  # Git ignore rules for Python, SQLite, and IDE files
├── README.md                   # Project documentation
├── static/
│   ├── style.css               # Apple HIG design system, glass effects, and animations
│   ├── libora_logo.png         # Libora brand logo
│   └── iit_sketch_bg.jpg       # Background architectural sketch
└── templates/
    ├── base.html               # Master layout, navigation capsule, Spotlight modal
    ├── home.html               # Main dashboard with inventory stats, catalog, and active issues
    ├── admin.html              # Admin portal: book entry, inventory overview, management
    ├── issue.html              # Book issue checkout workflow
    ├── receipt.html            # Printable receipt and return settlement
    └── components/
        └── book_logo.html      # Reusable brand SVG component
```

---

## 👤 Author

**RIT SARKAR**
- GitHub: [@ritsarkar](https://github.com/ritsarkar)
- Email: contactritsarkar@gmail.com

---

## 📄 License

This project is licensed under the MIT License.
