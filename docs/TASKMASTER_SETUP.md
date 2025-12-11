# Task Master AI Setup Guide

## ✅ What's Already Done
- Task Master AI directory structure created
- MCP configuration file created at `.cursor/mcp.json`
- Initial tasks created for MultiSportsBettingPlatform
- PRD document created

## 🔧 Next Steps to Complete Setup

### 1. Add Your API Keys
Edit `.cursor/mcp.json` and replace the placeholder API keys with your actual keys:

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-...",  // Your Claude API key
        "PERPLEXITY_API_KEY": "pplx-...",         // Your Perplexity API key (optional)
        "OPENAI_API_KEY": "sk-...",               // Your OpenAI API key (optional)
        // Remove or comment out keys you don't have
      }
    }
  }
}
```

### 2. Enable Task Master AI in Cursor
1. Open Cursor Settings (Ctrl+Shift+J)
2. Click on the MCP tab on the left
3. Enable "task-master-ai" with the toggle

### 3. Initialize Task Master AI
In Cursor's AI chat pane, say:
```
Initialize taskmaster-ai in my project
```

### 4. Start Using Task Master AI
Once initialized, you can use commands like:
- "What's the next task I should work on?"
- "Can you help me implement task 1?"
- "Show me tasks 1, 3, and 5"
- "Research the latest best practices for FastAPI authentication"

## 📋 Current Tasks Ready
1. Set up MultiSportsBettingPlatform Project Structure
2. Implement Head Agent Architecture  
3. Develop Sub-Agent System
4. Implement User Authentication and Session Management
5. Create Prediction Aggregation and Weighting System

## 🎯 Ready to Start Development!
Once you've added your API keys and enabled the MCP server, Task Master AI will be ready to help you build your MultiSportsBettingPlatform! 