"""
Chat history management with Supabase (RLS-safe)
All functions take a user-scoped Supabase Client (with JWT) to satisfy RLS.
"""

from datetime import datetime
from typing import List, Dict, Optional
import uuid
from supabase import Client

# --------------------------- Conversation Management ---------------------------

def create_new_conversation(sb: Client, user_id: str, title: Optional[str] = None) -> str:
    """Create a new conversation for a user."""
    conversation_id = str(uuid.uuid4())
    if not title:
        title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    sb.table('conversations').insert({
        'id': conversation_id,
        'user_id': user_id,  # must match auth.uid() in JWT
        'title': title,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }).execute()
    return conversation_id


def get_user_conversations(sb: Client, user_id: str, limit: int = 20) -> List[Dict]:
    """Get all conversations for a user, sorted by most recent."""
    result = sb.table('conversations')\
        .select('id,title,created_at,updated_at')\
        .eq('user_id', user_id)\
        .order('updated_at', desc=True)\
        .limit(limit)\
        .execute()

    conversations = []
    ids = [c['id'] for c in result.data] if result.data else []

    # last message & counts in a second pass (keeps select simple)
    for conv_id in ids:
        last = sb.table('messages')\
            .select('content')\
            .eq('conversation_id', conv_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        count = sb.table('messages').select('id', count='exact')\
            .eq('conversation_id', conv_id).execute()
        conversations.append({
            'id': conv_id,
            'title': next((c['title'] for c in result.data if c['id'] == conv_id), ''),
            'created_at': next((c['created_at'] for c in result.data if c['id'] == conv_id), None),
            'updated_at': next((c['updated_at'] for c in result.data if c['id'] == conv_id), None),
            'message_count': count.count if hasattr(count, 'count') else 0,
            'last_message': (last.data[0]['content'] if last.data else 'No messages')
        })
    return conversations


def update_conversation_timestamp(sb: Client, conversation_id: str):
    """Update the conversation's last updated timestamp."""
    sb.table('conversations').update({
        'updated_at': datetime.utcnow().isoformat()
    }).eq('id', conversation_id).execute()


def delete_conversation(sb: Client, conversation_id: str, user_id: str) -> bool:
    """Delete a conversation and all its messages."""
    try:
        sb.table('messages').delete().eq('conversation_id', conversation_id).execute()
        sb.table('conversations').delete().eq('id', conversation_id).eq('user_id', user_id).execute()
        return True
    except Exception:
        return False


# --------------------------- Message Management ---------------------------

def save_message(
    sb: Client,
    conversation_id: str,
    user_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict] = None
) -> str:
    """Save a message to the database."""
    message_id = str(uuid.uuid4())
    sb.table('messages').insert({
        'id': message_id,
        'conversation_id': conversation_id,
        'user_id': user_id,  # must match auth.uid() in JWT
        'role': role,
        'content': content,
        'metadata': metadata or {},
        'created_at': datetime.utcnow().isoformat()
    }).execute()

    update_conversation_timestamp(sb, conversation_id)
    return message_id


def get_conversation_history(sb: Client, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
    """Get all messages for a conversation."""
    query = sb.table('messages')\
        .select('*')\
        .eq('conversation_id', conversation_id)\
        .order('created_at', desc=False)
    if limit:
        query = query.limit(limit)
    res = query.execute()
    return res.data or []


def get_user_chat_history(sb: Client, user_id: str, limit: int = 50) -> List[Dict]:
    """Get recent chat history for a user across all conversations."""
    res = sb.table('messages')\
        .select('*')\
        .eq('user_id', user_id)\
        .order('created_at', desc=True)\
        .limit(limit)\
        .execute()
    return res.data or []
