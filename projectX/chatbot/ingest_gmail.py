import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag import add_document
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """
    Authenticate with Google and return Gmail service.
    First run will open browser for authentication.
    """
    creds = None

    # Load saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def extract_email_content(message):
    """
    Extract subject, from, date, and body from a Gmail message.
    """
    headers = message["payload"]["headers"]

    subject = next(
        (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
    )
    from_addr = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown")

    # Extract body (handle both plain text and multipart messages)
    body = ""

    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    body = base64.urlsafe_b64decode(data).decode(
                        "utf-8", errors="ignore"
                    )
                break
    else:
        data = message["payload"]["body"].get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return {
        "subject": subject,
        "from": from_addr,
        "date": date,
        "body": body,
        "message_id": message["id"],
    }


def ingest_emails(max_results=50):
    """
    Fetch emails from Gmail and add them to Supabase.

    Args:
        max_results: Number of emails to fetch (max 100)
    """
    print("📧 Starting Gmail ingestion...")

    try:
        service = get_gmail_service()
        print("✅ Connected to Gmail")

        # Get emails
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=min(max_results, 100))
            .execute()
        )

        messages = results.get("messages", [])
        print(f"📬 Found {len(messages)} emails to process")

        if not messages:
            print("ℹ️  No emails found")
            return

        # Text splitter for chunking long emails
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        success_count = 0

        for idx, msg_info in enumerate(messages, 1):
            try:
                # Get full message
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg_info["id"], format="full")
                    .execute()
                )

                email = extract_email_content(msg)

                # Create full document
                doc_text = f"Subject: {email['subject']}\nFrom: {email['from']}\nDate: {email['date']}\n\n{email['body']}"

                # Split into chunks if too long
                chunks = text_splitter.split_text(doc_text)

                # Add each chunk to database
                for chunk in chunks:
                    success = add_document(
                        text=chunk,
                        metadata={
                            "source": "gmail",
                            "subject": email["subject"],
                            "from": email["from"],
                            "date": email["date"],
                            "message_id": email["message_id"],
                        },
                    )
                    if success:
                        success_count += 1

                print(f"  [{idx}/{len(messages)}] ✅ {email['subject'][:50]}")

            except Exception as e:
                print(f"  [{idx}/{len(messages)}] ❌ Error: {str(e)}")

        print(f"\n✅ Ingestion complete! Added {success_count} email chunks")

    except FileNotFoundError:
        print("❌ credentials.json not found!")
        print("Please download it from Google Cloud Console and place in project root")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")


if __name__ == "__main__":
    ingest_emails(max_results=50)
