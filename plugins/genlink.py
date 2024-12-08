import re
import os
import json
import base64
import hashlib
import logging
from utils import temp
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id, save_batch_metadata  # Assuming this function exists

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# File: genlink.py
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_unique_id(base_id, sequence_number):
    """
    Generate a unique ID for files in the format [20 characters]+[sequence_number].
    This ensures batch identification for each file.
    """
    unique_part = hashlib.sha256(base_id.encode()).hexdigest()[:20]
    return f"{unique_part}+{sequence_number:02}"

def generate_batch_hash(batch_metadata):
    """
    Create a unique hash for the batch using SHA-256.
    The hash is 20 characters long and includes metadata for uniqueness.
    """
    hash_input = str(batch_metadata).encode()
    return hashlib.sha256(hash_input).hexdigest()[:20]

def save_batch_to_db(db, hash_code, user_id, metadata):
    """
    Save the batch metadata and hash to the database for persistence.
    """
    try:
        db.execute(
            "INSERT INTO batch_links (hash, user_id, metadata, created_at) VALUES (%s, %s, %s, %s)",
            (hash_code, user_id, metadata, datetime.now()),
        )
        db.commit()
        logger.info("Batch metadata saved to the database: %s", hash_code)
    except Exception as e:
        logger.exception("Failed to save batch metadata: %s", str(e))
        raise

def fetch_batch_from_db(db, hash_code):
    """
    Fetch batch metadata from the database using the hash.
    """
    try:
        result = db.fetch_one(
            "SELECT metadata FROM batch_links WHERE hash = %s", (hash_code,)
        )
        if result:
            logger.info("Fetched batch metadata for hash: %s", hash_code)
            return result[0]  # Metadata is stored as JSON
        else:
            logger.warning("No batch found for hash: %s", hash_code)
            return None
    except Exception as e:
        logger.exception("Failed to fetch batch metadata: %s", str(e))
        raise

def generate_shareable_link(base_url, batch_hash):
    """
    Generate a shareable link for the batch using the unique hash.
    """
    return f"{base_url}?start=BATCH-{batch_hash}"

def log_operation(operation, status, details=""):
    """
    Log bot operations with consistent formatting.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("[%s] %s - %s: %s", timestamp, operation, status, details)    with open(json_file, "w") as f:
        json.dump(outlist, f)

    # Generate Shortened `start` Parameter
    try:
        # New BATCH-specific format
        hash_code = hashlib.sha256(json.dumps(outlist).encode()).hexdigest()[:58]  # 58-char hash
        encoded_data = f"BATCH-{hash_code}"

        # Save batch metadata in the database
        await save_batch_metadata(message.from_user.id, outlist, encoded_data)

        # Generate Link
        await sts.edit(f"Link generated! Contains `{links_sent}` files: https://t.me/{temp.U_NAME}?start={encoded_data}")
        logger.info("Batch link generated for user: %s. Links Sent: %d", message.from_user.id, links_sent)
    except Exception as e:
        logger.exception("Failed to generate link for user: %s", message.from_user.id)
        await sts.edit("Failed to generate the link. Please try again.")
