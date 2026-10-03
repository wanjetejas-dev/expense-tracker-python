# expense-tracker-python
THIS IS A PROGRAM THAT CAN HELP YOU UP IN MANAGING YOUR DAILY EXPENSES
# 💰 Expense Tracker

A desktop **Expense Tracker** built with Python, Tkinter, MySQL, Matplotlib, and Requests.

The application allows users to record, update, delete, and view expenses. It also provides category-wise totals, monthly spending reports, a pie chart, and a live USD-to-INR exchange-rate feature.

## ✨ Features

- Add new expenses
- Update existing expenses
- Delete expenses
- Refresh the expense list
- Store data in MySQL
- Category-wise spending totals
- Monthly spending calculation
- Expense distribution pie chart
- USD → INR exchange-rate lookup
- Simple Tkinter graphical user interface
- Environment variables for database credentials

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Tkinter | GUI |
| MySQL | Database |
| mysql-connector-python | Python/MySQL connection |
| Matplotlib | Pie chart |
| Requests | Exchange-rate API |
| Git/GitHub | Version control and project hosting |

## 📁 Project Structure

```text
expense-tracker/
│
├── main.py
├── database.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Requirements

Install:

1. Python 3
2. MySQL Server
3. Git
4. Required Python packages from `requirements.txt`

Tkinter is normally included with standard Python installations on Windows.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/expense-tracker.git
cd expense-tracker
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database

Open MySQL Workbench or the MySQL command line and run:

```sql
SOURCE database.sql;
```

Or copy and execute the contents of `database.sql`.

This creates:

```text
Database: expense_tracker
Table: expenses
```

### 5. Configure database credentials

Create a `.env` file in the project directory.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=expense_tracker
```

⚠️ **Never commit `.env` to GitHub.**

The `.gitignore` file already excludes it.

### 6. Run the application

```bash
python main.py
```

## 🗄️ Database Structure

The `expenses` table contains:

| Column | Type | Description |
|---|---|---|
| id | INT | Primary key and auto-increment ID |
| date | DATE | Expense date |
| category | VARCHAR(100) | Expense category |
| description | VARCHAR(255) | Expense description |
| amount | DECIMAL(10,2) | Expense amount |

## 📊 Reports

### Category Totals

Displays the total amount spent in each category.

### Monthly Total

Calculates total spending for a selected month and year.

### Pie Chart

Displays the distribution of expenses by category using Matplotlib.

### Exchange Rate

Retrieves the latest available USD-to-INR exchange rate from an external exchange-rate API.

An internet connection is required for this feature.

## 🔐 Security

Database credentials are **not hard-coded** into the GitHub version of the project.

The application reads them from environment variables:

```text
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
```

Do not upload:

```text
.env
```

to GitHub.

## 🧪 Basic Usage

1. Start MySQL.
2. Start the application with `python main.py`.
3. Enter the date, category, description, and amount.
4. Click **Add**.
5. Select a row to load its values into the form.
6. Use **Update** or **Delete** when required.
7. Use the **Reports** buttons to analyze spending.

## 🐛 Troubleshooting

### MySQL connection error

Check:

- MySQL Server is running.
- Database `expense_tracker` exists.
- Username is correct.
- Password is correct.
- `.env` contains the correct values.

### `ModuleNotFoundError`

Install dependencies:

```bash
pip install -r requirements.txt
```

### Pie chart does not appear

Make sure Matplotlib is installed:

```bash
pip install matplotlib
```

### Exchange rate does not work

The exchange-rate feature requires an internet connection and access to the exchange-rate API.

## 📌 Future Improvements

Possible future enhancements:

- User login and authentication
- Budget limits
- Budget alerts
- Search and filtering
- Export reports to CSV/PDF
- Multiple currencies
- Dashboard with charts
- Date-range reports
- Backup and restore
- Better GUI styling

## 👨‍💻 Author

**Your Name**

Replace this with your name before publishing the repository.

## 📄 License

This project is provided for educational and college-project purposes. You may add an open-source license such as MIT if you want to make the reuse terms explicit.
