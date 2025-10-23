# Slack Timesheet Bot

A production-ready Slack bot for managing employee timesheets with automated reminders and reporting.

## Features

- 📝 **Interactive Timesheet Submission** using Slack Block Kit
- 🔢 **Dynamic Forms** (1-5 entries per submission)
- 📎 **Proof Upload** (images/PDFs)
- ⏰ **Weekly Reminders** (Every Friday)
- 📊 **Weekly & Monthly Reports** for managers
- 🗄️ **PostgreSQL Database** for data persistence
- 🐳 **Docker Support** for easy deployment
- ☁️ **AWS Ready** deployment configuration

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Reliable database
- **Slack SDK** - Official Slack integration
- **APScheduler** - Job scheduling
- **Docker** - Containerization
- **SQLAlchemy** - ORM

## Project Structure

```
slack-timesheet-bot/
├── app/
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── models/
│   │   └── timesheet.py        # Database models
│   ├── services/
│   │   ├── slack_service.py    # Slack API interactions
│   │   └── timesheet_service.py # Business logic
│   ├── handlers/
│   │   ├── interaction_handler.py # Handle Slack interactions
│   │   └── command_handler.py     # Handle Slack commands
│   ├── utils/
│   │   ├── block_builder.py    # Slack Block Kit builder
│   │   └── scheduler.py        # Scheduled tasks
│   └── routers/
│       └── slack_router.py     # API routes
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Setup Instructions

### 1. Prerequisites

- Docker & Docker Compose
- Slack Workspace with admin access
- ngrok (for local development)

### 2. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Timesheet Bot"
4. Select your workspace

### 3. Configure Slack App

**OAuth & Permissions:**
- Add Bot Token Scopes:
  - `chat:write`
  - `commands`
  - `users:read`
  - `channels:read`
  - `files:read`
  - `im:write`
  - `channels:history`

**Slash Commands:**
Create these commands:
- `/timesheet` → Request URL: `https://your-domain/slack/commands/timesheet`
- `/timesheetWeekly` → Request URL: `https://your-domain/slack/commands/timesheet-weekly`
- `/timesheetMonthly` → Request URL: `https://your-domain/slack/commands/timesheet-monthly`

**Interactivity:**
- Enable Interactivity
- Request URL: `https://your-domain/slack/interactions`

**Event Subscriptions:**
- Enable Events
- Request URL: `https://your-domain/slack/events`

### 4. Environment Setup

Create `.env` file:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_MANAGER_USER_ID=U01234567  # Manager's Slack User ID

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/timesheet_db

# Application Configuration
APP_ENV=production
LOG_LEVEL=INFO
```

### 5. Local Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 6. Expose Local Server (Development)

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start ngrok
ngrok http 8000

# Use the HTTPS URL in Slack App configuration
```

## AWS Deployment

### Option 1: AWS ECS (Recommended)

1. **Build and push Docker image:**
```bash
aws ecr create-repository --repository-name slack-timesheet-bot
docker build -t slack-timesheet-bot .
docker tag slack-timesheet-bot:latest <account-id>.dkr.ecr.<region>.amazonaws.com/slack-timesheet-bot:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/slack-timesheet-bot:latest
```

2. **Create RDS PostgreSQL instance**
3. **Deploy to ECS Fargate**
4. **Configure Application Load Balancer**
5. **Update Slack App URLs with ALB domain**

### Option 2: AWS EC2

1. **Launch EC2 instance** (t3.small or larger)
2. **Install Docker & Docker Compose**
3. **Clone repository**
4. **Configure environment variables**
5. **Run with docker-compose**
6. **Configure security groups** (allow ports 80, 443, 8000)

### Option 3: AWS Lambda + API Gateway

For serverless deployment, see `docs/lambda-deployment.md`

## Usage

### Submit Timesheet

1. Type `/timesheet` in any channel
2. Select number of entries (1-5)
3. Fill in details:
   - Client name
   - Hours worked
   - Upload proof (optional)
4. Click "Submit Timesheet"
5. Receive confirmation DM

### View Reports (Managers Only)

- **Weekly:** `/timesheetWeekly`
- **Monthly:** `/timesheetMonthly`

### Automated Reminders

- **Every Friday 10 AM:** All users receive reminder
- **Last day of month 5 PM:** Manager receives monthly summary

## Database Schema

```sql
CREATE TABLE timesheet_entries (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    channel_id VARCHAR(50) NOT NULL,
    client_name VARCHAR(200) NOT NULL,
    hours FLOAT NOT NULL,
    proof_url TEXT,
    submission_date TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_id ON timesheet_entries(user_id);
CREATE INDEX idx_submission_date ON timesheet_entries(submission_date);
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /slack/events` - Slack events
- `POST /slack/interactions` - Slack interactions
- `POST /slack/commands/timesheet` - Timesheet command
- `POST /slack/commands/timesheet-weekly` - Weekly report
- `POST /slack/commands/timesheet-monthly` - Monthly report

## Monitoring & Logging

Logs are structured and include:
- Request/response tracking
- Error handling
- Scheduler job execution
- Database operations

View logs:
```bash
docker-compose logs -f app
```

## Troubleshooting

### Bot not responding
- Check if bot is added to channel
- Verify Request URLs in Slack App config
- Check logs for errors

### Database connection issues
```bash
docker-compose exec db psql -U postgres -d timesheet_db
```

### Scheduler not working
- Check timezone configuration
- Verify scheduler logs
- Test manually: `docker-compose exec app python -c "from app.utils.scheduler import TaskScheduler; import asyncio; s = TaskScheduler(); asyncio.run(s.send_weekly_reminder())"`

## Security Best Practices

✅ Signature verification for all Slack requests
✅ Environment variables for sensitive data
✅ SQL injection prevention via ORM
✅ Rate limiting on endpoints
✅ HTTPS only in production
✅ Secrets rotation policy

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

MIT License - see LICENSE file

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourorg/slack-timesheet-bot/issues
- Email: support@yourcompany.com

---
