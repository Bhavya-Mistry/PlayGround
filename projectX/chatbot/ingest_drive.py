import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag import add_document
from dotenv import load_dotenv
import io

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    """Authenticate with Google Drive."""
    creds = None

    if os.path.exists("token_drive.pickle"):
        with open("token_drive.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token_drive.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


def ingest_drive_files(max_results=20):
    """
    Fetch text files from Google Drive and add to Supabase.

    Args:
        max_results: Number of files to fetch
    """
    print("📄 Starting Google Drive ingestion...")

    try:
        service = get_drive_service()
        print("✅ Connected to Google Drive")

        # Search for text/document files
        query = "mimeType='text/plain' or mimeType='application/pdf' or mimeType='application/vnd.google-apps.document'"
        results = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name, modifiedTime, webViewLink)",
                pageSize=min(max_results, 100),
            )
            .execute()
        )

        files = results.get("files", [])
        print(f"📂 Found {len(files)} files to process")

        if not files:
            print("ℹ️  No files found")
            return

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        success_count = 0

        for idx, file in enumerate(files, 1):
            try:
                file_id = file["id"]
                file_name = file["name"]
                modified = file["modifiedTime"]

                # Export as text (works for Docs, PDFs, etc.)
                request = service.files().export_media(
                    fileId=file_id, mimeType="text/plain"
                )

                content = request.execute().decode("utf-8", errors="ignore")

                # Split into chunks
                chunks = text_splitter.split_text(content)

                for chunk in chunks:
                    success = add_document(
                        text=chunk,
                        metadata={
                            "source": "drive",
                            "subject": file_name,
                            "from": "Google Drive",
                            "date": modified,
                            "file_id": file_id,
                        },
                    )
                    if success:
                        success_count += 1

                print(f"  [{idx}/{len(files)}] ✅ {file_name}")

            except Exception as e:
                print(f"  [{idx}/{len(files)}] ⚠️  {file['name']}: {str(e)}")

        print(f"\n✅ Drive ingestion complete! Added {success_count} file chunks")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    ingest_drive_files(max_results=20)
