# Wallet Engine - Secure Digital Wallet System

A modern, secure digital wallet transaction engine with AI-powered voice assistance. Built with FastAPI, PostgreSQL, and featuring industry-standard cryptographic security.

## 🌟 Features

### Core Wallet Operations
- **User Management**: Create and manage user accounts
- **Wallet Management**: Create wallets with secure PIN authentication
- **Deposits**: Add funds to wallets with PIN verification
- **Transfers**: Send money between wallets (single and batch transfers)
- **Balance Checking**: Real-time wallet balance queries
- **Transaction History**: Complete audit trail of all transactions

### 🎤 AI Voice Assistant
- **Natural Language Processing**: Speak commands in plain English
- **Voice Recognition**: Web Speech API integration
- **Text-to-Speech**: AI responds with voice feedback
- **Autonomous Operations**: Execute wallet operations via voice commands
- **Security-Aware**: PINs are masked in voice responses

### 🔐 Security Features
- **Bcrypt PIN Hashing**: Industry-standard password hashing
- **Secure Verification**: Constant-time comparison prevents timing attacks
- **Rate Limiting**: Brute force attack prevention
- **Atomic Transactions**: Database-level transaction safety
- **PIN Authentication**: All sensitive operations require PIN verification

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern Python web framework for APIs
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: ORM for database operations
- **Bcrypt**: Cryptographic hashing for PINs
- **Uvicorn**: ASGI server

### Frontend Stack
- **HTML5/CSS3**: Modern web interface
- **Vanilla JavaScript**: No framework dependencies
- **Web Speech API**: Voice recognition and synthesis
- **Responsive Design**: Mobile-friendly UI

### Project Structure
```
builttobreak-master/
├── app/
│   ├── api/              # API route handlers
│   │   ├── users.py      # User management endpoints
│   │   ├── wallets.py    # Wallet operations endpoints
│   │   └── transfer.py   # Transfer endpoints
│   ├── core/             # Core utilities
│   │   ├── crypto.py     # Cryptographic functions
│   │   └── rate_limiter.py # Rate limiting
│   ├── crud/             # Database operations
│   │   ├── user.py       # User CRUD operations
│   │   ├── wallet.py     # Wallet CRUD operations
│   │   └── transaction.py # Transaction CRUD operations
│   ├── database/         # Database configuration
│   │   ├── db.py         # Database connection
│   │   └── models.py     # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py       # User schemas
│   │   ├── wallet.py     # Wallet schemas
│   │   └── transaction.py # Transaction schemas
│   └── main.py           # Application entry point
├── ui/                   # Frontend files
│   ├── index.html        # Dashboard
│   ├── voice-assistance.html # AI Voice Assistant
│   ├── voice-assistant.js # Voice AI logic
│   ├── style.css         # Styling
│   └── script.js         # UI interactions
├── tests/                # Test suite
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
└── migrate_pins.py       # Security migration script
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Docker Compose

### Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd builttobreak-master
```

2. **Start the application**
```bash
docker-compose up --build
```

3. **Access the application**
- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Voice Assistant**: http://localhost:8000/voice-assistance

### First-Time Setup

The application will automatically:
- Create database tables
- Initialize PostgreSQL database
- Start the FastAPI server

## 📡 API Endpoints

### User Management
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/{user_id}` - Get user details

### Wallet Operations
- `POST /api/v1/wallets/` - Create a new wallet (requires PIN)
- `GET /api/v1/wallets/` - List all wallets
- `GET /api/v1/wallets/{wallet_id}` - Get wallet details
- `POST /api/v1/wallets/deposit` - Deposit funds (requires PIN)

### Transfers
- `POST /api/v1/transfer/` - Single transfer (requires PIN)
- `POST /api/v1/transfer/batch` - Batch transfer (requires PIN)
- `GET /api/v1/transfer/transactions` - Get transaction history

## 🎤 Voice Assistant Usage

### Getting Started
1. Navigate to http://localhost:8000/voice-assistance
2. Click the microphone button
3. Grant microphone permissions
4. Speak your command

### Example Voice Commands

**User Management:**
- "Create user named Alice with email alice@example.com"
- "Show all users"

**Wallet Operations:**
- "Create wallet for user 1 with PIN 1234"
- "Show all wallets"
- "Check balance for wallet 1"

**Transactions:**
- "Deposit $100 to wallet 1 with PIN 1234"
- "Transfer $50 from wallet 1 to wallet 2 with PIN 1234"
- "Show transactions"

**Help:**
- "Help" - Shows available commands

## 🔧 Major Operations

### 1. Creating a User
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com"}'
```

### 2. Creating a Wallet
```bash
curl -X POST http://localhost:8000/api/v1/wallets/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "pin": "1234"}'
```

### 3. Depositing Funds
```bash
curl -X POST http://localhost:8000/api/v1/wallets/deposit \
  -H "Content-Type: application/json" \
  -d '{"wallet_id": 1, "amount": 500.00, "pin": "1234"}'
```

### 4. Transferring Money
```bash
curl -X POST http://localhost:8000/api/v1/transfer/ \
  -H "Content-Type: application/json" \
  -d '{
    "from_wallet_id": 1,
    "to_wallet_id": 2,
    "amount": 100.00,
    "pin": "1234"
  }'
```

## 🔐 Security Implementation

### PIN Security
- All PINs are hashed using **bcrypt** with automatic salting
- Secure verification with constant-time comparison
- PINs are never stored in plaintext
- Voice assistant masks PINs in responses

### Rate Limiting
- 5 PIN verification attempts per minute per IP
- 100 general API requests per minute
- 10 transfers per minute per IP

### Transaction Safety
- Database-level locking prevents race conditions
- Atomic batch transfers (all-or-nothing)
- PIN authentication required for all sensitive operations

## 🛠️ Development

### Running Tests
```bash
python tests/test_failures.py
```

### Database Reset
```bash
# Windows
reset_db.bat

# Linux/Mac
./reset_db.sh
```

### Security Migration
If upgrading from an older version:
```bash
python migrate_pins.py
```

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address

### Wallets Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `balance`: Current balance
- `pin_hash`: Bcrypt hashed PIN
- `status`: ACTIVE/INACTIVE

### Transactions Table
- `id`: Primary key
- `from_wallet_id`: Sender wallet
- `to_wallet_id`: Receiver wallet
- `amount`: Transaction amount
- `timestamp`: Transaction time

## 🌐 Browser Compatibility

### Voice Assistant
- ✅ **Chrome** (Recommended)
- ✅ **Edge**
- ⚠️ **Firefox** (Limited support)
- ⚠️ **Safari** (Limited support)

## 📝 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `API_PORT`: API server port (default: 8000)

### Docker Configuration
- Web service: Port 8000
- Database service: PostgreSQL 15
- Volume: Persistent data storage

## 🤝 Contributing

This project was developed for educational purposes and hackathon demonstration.

## 📄 License

This project is for educational and demonstration purposes.

## 🎯 Hackathon Features

Perfect for demonstrating:
- ✅ Modern API design with FastAPI
- ✅ AI-powered voice interfaces
- ✅ Cryptographic security implementation
- ✅ Real-time transaction processing
- ✅ Natural language processing
- ✅ Responsive web design
- ✅ Docker containerization
- ✅ Database design and optimization

## 🚨 Troubleshooting

### Docker Issues
```bash
# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Database Connection Issues
- Ensure PostgreSQL container is running
- Check docker-compose logs: `docker-compose logs db`

### Voice Assistant Not Working
- Use Chrome or Edge browser
- Grant microphone permissions
- Check browser console for errors

## 📞 Support

For issues or questions, please check:
- API Documentation: http://localhost:8000/docs
- Application logs: `docker-compose logs web`
- Database logs: `docker-compose logs db`

---

**Built with ❤️ for secure, intelligent wallet management**
