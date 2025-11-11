# Meta Ads MCP Server

An MCP (Model Context Protocol) server that enables AI assistants like Claude and Cursor to interact with Meta Ads (Facebook/Instagram) programmatically through natural language conversations.

## What This Does

This MCP server allows you to:
- View your Meta ad accounts and their details
- Create, read, update, and manage ad campaigns
- Get performance analytics and insights
- Search for targeting interests, demographics, and locations
- Receive AI-powered campaign analysis and recommendations

All operations run locally on your machine for maximum security and privacy.

## Prerequisites

- Python 3.10 or higher
- A Meta Ads account with API access
- A Facebook App configured for Marketing API access

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd meta-ads-mcp
```

Replace `<repository-url>` with the actual GitHub repository URL.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required Python packages including FastAPI, Facebook Business SDK, and other dependencies.

### Step 3: Set Up Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new app or use an existing one
3. Add the **Marketing API** product to your app
4. In your app settings, add `http://localhost:8000/auth/facebook/callback` as a valid OAuth redirect URI
5. Note down your **App ID** and **App Secret**

### Step 4: Configure Environment

Copy the example configuration file:

```bash
cp env.example .env
```

Edit the `.env` file with your credentials:

```bash
# Open .env in a text editor and fill in these required values:

# Your Facebook App ID from Step 3
FB_APP_ID=1234567890123456

# Your Facebook App Secret from Step 3
FB_APP_SECRET=your_app_secret_here

# Enable OAuth authentication
FB_OAUTH_ENABLED=true

# The redirect URI you added to your Facebook App
FB_REDIRECT_URI=http://localhost:8000/auth/facebook/callback
```

### Step 5: Generate Access Token

Run the OAuth web server to authenticate:

```bash
# Terminal 1: Start the OAuth web server
python src/auth/run_web_server.py
```

This starts a local web server on port 8000. Leave this running.

### Step 6: Authenticate with Facebook

1. Open your browser and go to: `http://localhost:8000/auth/facebook`
2. Click the "Connect Facebook" link
3. Log in to Facebook if prompted
4. Grant permissions to your app
5. You will be redirected to a success page showing your connected ad accounts

The access token is now stored securely in a local database.

### Step 7: Start the MCP Server

```bash
# Terminal 2: Start the MCP server
python src/server.py
```

This starts the MCP server that Claude/Cursor will connect to. Leave this running.

## Configure Claude Desktop

Add the Meta Ads MCP server to your Claude Desktop configuration:

### On macOS/Linux:
```bash
# Create or edit the configuration file
nano ~/.config/Claude/claude_desktop_config.json
```

### On Windows:
```bash
# Create or edit the configuration file
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration to the file:

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "python",
      "args": ["/full/path/to/meta-ads-mcp/src/server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/meta-ads-mcp/src"
      }
    }
  }
}
```

Replace `/full/path/to/meta-ads-mcp` with the actual path to your cloned repository.

## Configure Cursor

Add the Meta Ads MCP server to your Cursor MCP configuration:

### Method 1: GUI Configuration
1. Open Cursor settings
2. Go to the MCP section
3. Add a new MCP server with these settings:

```
Name: Meta Ads
Type: Command
Command: python
Arguments: /full/path/to/Meta_ads_mcp/src/server.py
Environment Variables:
  DATABASE_URL=sqlite:////full/path/to/.meta-ads-mcp/oauth.db
```

### Method 2: Configuration File (Alternative)

If you prefer editing the configuration file directly, add this to your Cursor MCP config:

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "python",
      "args": [
        "/full/path/to/Meta_ads_mcp/src/server.py"
      ],
      "env": {
        "DATABASE_URL": "sqlite:///full/path/to/.meta-ads-mcp/oauth.db"
      }
    }
  }
}
```

**Note:** Adjust the paths if you move the repository to a different location.

## Verify Installation

Restart Claude Desktop or Cursor to load the new MCP configuration.

Test that it's working by asking Claude/Cursor:

```
"Show me my Meta ad accounts"
```

You should see a response listing your connected ad accounts with their details.

## Usage Examples

Once configured, you can interact with your Meta Ads through natural language:

### View Accounts
```
"List all my ad accounts"
"Show me account act_123456789 details"
```

### Manage Campaigns
```
"Create a new campaign called 'Summer Sale' with $100 daily budget for OUTCOME_SALES"
"Show me all active campaigns in account act_123456789"
"Pause campaign 120202345678901234"
"Update campaign 120202345678901234 to have $200 daily budget"
```

### Analytics
```
"How did my campaigns perform last week?"
"Get insights for campaign 120202345678901234 from the last 30 days"
"Analyze my campaigns and tell me which ones to optimize"
```

### Targeting
```
"Search for interests related to 'coffee'"
"Find demographic options for age groups"
"Search for locations in 'United States'"
```

## Troubleshooting

### "No access token available"

1. Check that the OAuth web server (Terminal 1) is still running
2. Verify you completed the Facebook authentication flow
3. Try clearing the database and re-authenticating:

```bash
python scripts/clear_database.py
# Then repeat Steps 5-6
```

### "Connection refused" or "MCP server not responding"

1. Ensure both servers are running:
   - OAuth web server: `python src/auth/run_web_server.py`
   - MCP server: `python src/server.py`

2. Check that the paths in your MCP configuration are correct

3. Verify Python is in your PATH

### "Facebook login not working"

1. Check your `.env` file has the correct:
   - `FB_APP_ID`
   - `FB_APP_SECRET`
   - `FB_REDIRECT_URI=http://localhost:8000/auth/facebook/callback`

2. Verify the redirect URI is added to your Facebook App settings

3. Ensure the OAuth web server is running on port 8000

### "Permission denied" errors

Your Facebook access token needs these permissions:
- `ads_management` - Create and modify campaigns
- `ads_read` - Read campaign data
- `read_insights` - Access performance metrics

Regenerate your token in Facebook Developers if needed.

### Port 8000 already in use

Change the web server port in your `.env` file:

```bash
WEB_SERVER_PORT=8001
FB_REDIRECT_URI=http://localhost:8001/auth/facebook/callback
```

Then update your Facebook App redirect URI to match.

### Database issues

Clear and reset the database:

```bash
# Clear tokens only
python scripts/clear_database.py

# Full database reset
python scripts/clear_database.py --reset
```

## Available MCP Tools

The server provides these tools to Claude/Cursor:

### Account Management
- `get_ad_accounts` - List all accessible ad accounts
- `get_account_info` - Get detailed account information

### Campaign Management
- `get_campaigns` - List campaigns with filtering
- `get_campaign_details` - Get campaign information
- `create_campaign` - Create new campaigns
- `update_campaign` - Update campaign settings

### Analytics
- `get_insights` - Get performance metrics
- `analyze_campaigns` - AI-powered analysis

### Targeting
- `search_interests` - Find interest-based targeting
- `search_demographics` - Find demographic targeting
- `search_locations` - Find geographic targeting

### Database Management
- `clear_database` - Clear stored tokens
- `reset_database` - Reset entire database
- `token_status` - Check token status
- `db_config` - View database configuration

## Security Notes

- Access tokens are encrypted and stored locally on your machine
- No data is sent to external servers
- Each user configures their own Facebook App credentials
- The MCP server runs entirely on your local machine

## Support

For issues:
1. Check the troubleshooting section above
2. Verify your Facebook App configuration
3. Ensure both servers are running
4. Check the server logs for error messages

The servers log to stderr, so check your terminal output for error details.