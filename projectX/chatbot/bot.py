import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from rag import ask_jarvis, get_db_stats

load_dotenv()

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", help_command=None, intents=intents)


@bot.event
async def on_ready():
    """Called when bot is ready."""
    print(f"✅ Jarvis is online as {bot.user}")
    stats = get_db_stats()
    print(f"📊 Database: {stats['status']}")
    print(f"📚 Documents: {stats['total_documents']}")


@bot.command(name="ask")
async def ask_command(ctx, *, question):
    """
    Ask Jarvis a question.

    Usage: !ask What emails did I get today?
    """
    async with ctx.typing():
        try:
            answer, sources = ask_jarvis(question)

            # Format response
            response = f"**Q:** {question}\n\n**A:** {answer}\n\n"

            if sources:
                response += "**📌 Sources:**\n"
                for i, doc in enumerate(sources, 1):
                    subject = doc.get("subject", "No subject")
                    source = doc.get("source", "Unknown").upper()
                    response += f"{i}. [{source}] {subject}\n"

            # Split long messages
            if len(response) > 2000:
                # Send the message in chunks of 1900 characters so nothing is cut off
                for i in range(0, len(response), 1900):
                    await ctx.send(response[i : i + 1900])
            else:
                await ctx.send(response)

        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name="status")
async def status_command(ctx):
    """Check Jarvis status."""
    stats = get_db_stats()
    embed = discord.Embed(
        title="🤖 Jarvis Status",
        description=stats["status"],
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="📚 Documents", value=str(stats["total_documents"]), inline=False
    )
    embed.add_field(name="💾 Database", value="Supabase", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="help")
async def help_command(ctx):
    """Show help message."""
    embed = discord.Embed(
        title="🤖 Jarvis - Personal AI Assistant",
        description="Your context-aware personal AI with access to all your data",
        color=discord.Color.purple(),
    )
    embed.add_field(
        name="!ask <question>",
        value="Ask Jarvis anything about your data",
        inline=False,
    )
    embed.add_field(name="!status", value="Check Jarvis status", inline=False)
    embed.add_field(
        name="Example", value="!ask What emails did I get from Sarah?", inline=False
    )
    await ctx.send(embed=embed)


# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not set in .env")
    else:
        bot.run(token)
