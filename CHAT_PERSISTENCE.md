# Chat Persistence Setup Guide

This guide will help you set up conversation persistence for your LegaBot application.

## 📋 Overview

The chat persistence system stores:
- **Conversations**: Individual chat sessions for each user
- **Messages**: All questions and answers within conversations
- **Metadata**: Additional information like timestamps, sources, etc.

## 🗄️ Database Setup

### Step 1: Run the Migration

1. Go to your **Supabase Dashboard**
2. Navigate to **SQL Editor**
3. Copy the entire content from `migrations/create_chat_history_tables.sql`
4. Paste it into the SQL Editor
5. Click **Run** to execute the migration

This will create:
- `conversations` table
- `messages` table
- Indexes for performance
- Row Level Security (RLS) policies
- Helpful views and functions

### Step 2: Verify Tables

After running the migration, verify in **Table Editor**:

✅ **conversations** table with columns:
- `id` (UUID, Primary Key)
- `user_id` (UUID, Foreign Key to auth.users)
- `title` (TEXT)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)
- `metadata` (JSONB)

✅ **messages** table with columns:
- `id` (UUID, Primary Key)
- `conversation_id` (UUID, Foreign Key to conversations)
- `user_id` (UUID, Foreign Key to auth.users)
- `role` (TEXT: 'user' or 'assistant')
- `content` (TEXT)
- `metadata` (JSONB)
- `created_at` (TIMESTAMPTZ)

## 📁 File Structure

Ensure you have these files in your project:

```
legabot/
├── src/
│   ├── ui/
│   │   └── app.py                    # Updated UI with persistence
│   ├── db/
│   │   ├── __init__.py              # Empty init file
│   │   └── chat_history.py          # Chat persistence module
│   └── auth/
│       └── auth_service.py           # Your existing auth
├── migrations/
│   └── create_chat_history_tables.sql
└── .env
```

### Create the db folder

```bash
mkdir -p src/db
touch src/db/__init__.py
```

## 🔧 Configuration

### Environment Variables

Ensure your `.env` file has:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### Install Dependencies

```bash
pip install supabase-py
```

## ✨ Features Enabled

### 1. **Automatic Chat Saving**
- Every user message is automatically saved
- Every assistant response is automatically saved
- Timestamps are tracked

### 2. **Conversation Management**
- New conversation created on login
- "New Chat" button to start fresh conversations
- Conversations automatically updated with new messages

### 3. **History Viewing**
- "📜 History" button shows all past conversations
- Click any conversation to load its complete history
- Messages displayed in chronological order

### 4. **User Actions**

New action buttons available:
- **💡 Examples**: Quick example questions
- **📜 History**: View all conversations
- **➕ New Chat**: Start a new conversation
- **👤 Profile**: View profile with stats
- **🚪 Logout**: Sign out

## 🎯 Usage Guide

### For Users

1. **Start Chatting**: Messages are automatically saved
2. **View History**: Click "📜 History" to see past conversations
3. **Load Conversation**: Click "Load Conv X" to restore a chat
4. **New Chat**: Click "➕ New Chat" to start fresh
5. **Profile**: View total conversations and messages

### For Developers

#### Save a Message
```python
from src.db.chat_history import save_message

message_id = save_message(
    conversation_id="conv-uuid",
    user_id="user-uuid",
    role="user",  # or "assistant"
    content="What is theft under IPC?",
    metadata={"sources": ["IPC Section 378"]}
)
```

#### Get Conversation History
```python
from src.db.chat_history import get_conversation_history

messages = get_conversation_history("conv-uuid")
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")
```

#### List User Conversations
```python
from src.db.chat_history import get_user_conversations

conversations = get_user_conversations("user-uuid")
for conv in conversations:
    print(f"{conv['title']} - {conv['message_count']} messages")
```

## 🔒 Security Features

### Row Level Security (RLS)

✅ Users can only:
- View their own conversations and messages
- Create messages in their own conversations
- Update/delete their own data

✅ Automatic protections:
- User ID validation on all operations
- Foreign key constraints
- Cascade deletes (deleting conversation removes all messages)

## 📊 Database Performance

### Indexes Created

- `conversations`: indexed on `user_id`, `updated_at`
- `messages`: indexed on `conversation_id`, `user_id`, `created_at`
- Full-text search index on message content

### Query Optimization

The system uses:
- Efficient joins for conversation summaries
- Pagination support (limit parameter)
- Descending order for recent-first queries

## 🧪 Testing

### Test the System

1. **Login** to your account
2. **Ask a question**: "What is theft under IPC?"
3. **Get a response**: Should see the answer
4. **Click History**: Should see your conversation listed
5. **Start New Chat**: Should create a fresh conversation
6. **Load History**: Should restore your previous chat

### Verify in Database

Go to Supabase **Table Editor**:

1. Check `conversations` table - should have entries
2. Check `messages` table - should have user and assistant messages
3. Verify `user_id` matches your auth user

## 🐛 Troubleshooting

### Issue: "Table does not exist"

**Solution**: Run the migration SQL in Supabase SQL Editor

### Issue: "Permission denied"

**Solution**: Check RLS policies are enabled:
```sql
-- Verify RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('conversations', 'messages');
```

### Issue: Messages not saving

**Solution**: Check Supabase connection:
```python
from src.db.chat_history import supabase
print(supabase.table('conversations').select('*').limit(1).execute())
```

### Issue: Import errors

**Solution**: Ensure folder structure is correct:
```bash
# Create __init__.py files
touch src/__init__.py
touch src/db/__init__.py
```

## 🚀 Advanced Features

### Search Messages
```python
from src.db.chat_history import search_messages

results = search_messages(user_id, "theft")
```

### Get User Statistics
```python
from src.db.chat_history import get_user_stats

stats = get_user_stats(user_id)
print(f"Total conversations: {stats['total_conversations']}")
print(f"Total messages: {stats['total_messages']}")
```

### Delete Old Conversations
```sql
-- In Supabase SQL Editor
SELECT delete_old_conversations(365); -- Delete conversations older than 1 year
```

## 📈 Monitoring

### Check Storage Usage

```sql
-- Count total conversations
SELECT COUNT(*) FROM conversations;

-- Count total messages
SELECT COUNT(*) FROM messages;

-- Average messages per conversation
SELECT AVG(message_count) FROM conversation_summaries;

-- Most active users
SELECT user_id, COUNT(*) as conversation_count
FROM conversations
GROUP BY user_id
ORDER BY conversation_count DESC
LIMIT 10;
```

## 🎨 UI Improvements

The updated UI includes:

- ✅ Automatic message persistence
- ✅ Conversation history browser
- ✅ One-click conversation loading
- ✅ New chat functionality
- ✅ Enhanced profile with statistics
- ✅ Better visual formatting
- ✅ Clear action buttons

## 📝 Notes

- Conversations are automatically created on login
- Each chat session gets a unique conversation ID
- Messages are saved in real-time
- History is preserved across sessions
- Users can have multiple active conversations

## 🆘 Support

If you encounter issues:

1. Check Supabase connection in `.env`
2. Verify migration ran successfully
3. Check browser console for errors
4. Verify RLS policies are active
5. Test with a fresh user account

---

**Congratulations! 🎉** Your LegaBot now has persistent conversations!

Users can now:
- Chat with confidence knowing history is saved
- Review past conversations anytime
- Switch between multiple chat sessions
- Track their usage statistics