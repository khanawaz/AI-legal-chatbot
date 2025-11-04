import sys
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

# 👇 Add these 3 lines so Python can find "src"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import chainlit as cl
from src.llm.rag_pipeline import get_legal_answer

# 🏁 When chat starts
@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "👋 **Welcome to LegaBot!**\n\n"
            "I’m your Indian legal research assistant. Ask me anything about IPC, CrPC, or landmark judgments.\n\n"
            "💡 **Example Questions:**\n"
            "- What is theft under IPC?\n"
            "- Punishment for murder?\n"
            "- What section deals with bail?\n\n"
            "Type your question below 👇"
        )
    ).send()

# 💬 When a message is received
@cl.on_message
async def main(message: cl.Message):
    query = message.content.strip()

    # Allow user to exit gracefully
    if query.lower() in ["exit", "quit"]:
        await cl.Message(content="👋 Thank you for using LegaBot!").send()
        return

    await cl.Message(content="🔍 Searching legal documents...").send()
    answer = get_legal_answer(query)

    await cl.Message(content=answer).send()