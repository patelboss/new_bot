import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import *
from utils import get_settings, save_group_settings
from datetime import datetime
import hashlib
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

sec_client = MongoClient(SEC_FILE_DB_URI)
sec_db = sec_client[DATABASE_NAME]
sec_col = sec_db[COLLECTION_NAME]


async def save_file(media):
    """Save file in database"""

    logger.info("Saving file with ID: %s", media.file_id)
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    found1 = {'file_name': file_name}
    check = col.find_one(found1)
    if check:
        logger.warning("File %s is already saved in main collection.", file_name)
        return False, 0
    check2 = sec_col.find_one(found1)
    if check2:
        logger.warning("File %s is already saved in secondary collection.", file_name)
        return False, 0
    file = {
        'file_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': media.caption.html if media.caption else None
    }
    result = db.command('dbstats')
    data_size = result['dataSize']
    if data_size > 503316480:
        logger.info("Database size is over 500MB, saving to secondary collection.")
        found = {'file_id': file_id}
        check = col.find_one(found)
        if check:
            logger.warning("File %s is already saved.", file_name)
            return False, 0
        else:
            try:
                sec_col.insert_one(file)
                logger.info("File %s successfully saved in secondary collection.", file_name)
                return True, 1
            except DuplicateKeyError:      
                logger.warning("File %s is already saved in secondary collection.", file_name)
                return False, 0
    else:
        try:
            col.insert_one(file)
            logger.info("File %s successfully saved in main collection.", file_name)
            return True, 1
        except DuplicateKeyError:      
            logger.warning("File %s is already saved in main collection.", file_name)
            return False, 0


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    logger.info("Fetching search results for query: '%s'", query)
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        logger.error("Invalid query pattern: '%s'", query)
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if MULTIPLE_DATABASE:
        result1 = col.count_documents(filter)
        result2 = sec_col.count_documents(filter)
        total_results = result1 + result2
    else:
        total_results = col.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ""

    if MULTIPLE_DATABASE:
        cursor1 = col.find(filter)
        cursor2 = sec_col.find(filter)
    else:
        cursor = col.find(filter)
    
    if MULTIPLE_DATABASE:
        cursor1.skip(offset).limit(max_results)
        cursor2.skip(offset).limit(max_results)
    else:
        cursor.skip(offset).limit(max_results)

    if MULTIPLE_DATABASE:
        files1 = list(cursor1)
        files2 = list(cursor2)
        files = files1 + files2
    else:
        files = list(cursor)

    logger.info("Search complete. Found %d files.", len(files))
    return files, next_offset, total_results


async def get_bad_files(query, file_type=None, filter=False):
    """For given query return (results, next_offset)"""
    logger.info("Fetching bad files for query: '%s'", query)
    query = query.strip()

    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        logger.error("Invalid bad file query pattern: '%s'", query)
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    if MULTIPLE_DATABASE:
        result1 = col.count_documents(filter)
        result2 = sec_col.count_documents(filter)
        total_results = result1 + result2
    else:
        total_results = col.count_documents(filter)

    if MULTIPLE_DATABASE:
        cursor1 = col.find(filter)
        cursor2 = sec_col.find(filter)
    else:
        cursor = col.find(filter)

    if MULTIPLE_DATABASE:
        files1 = list(cursor1)
        files2 = list(cursor2)
        files = files1 + files2
    else:
        files = list(cursor)

    logger.info("Bad file search complete. Found %d files.", len(files))
    return files, total_results


async def get_file_details(query):
    logger.info("Fetching file details for file_id: %s", query)
    filter = {'file_id': query}
    filedetails = col.find_one(filter)
    if not filedetails:
        filedetails = sec_col.find_one(filter)
    if filedetails:
        logger.info("File details found: %s", filedetails)
    else:
        logger.warning("File with ID %s not found.", query)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    encoded_id = base64.urlsafe_b64encode(r).decode().rstrip("=")
    logger.debug("Encoded file ID: %s", encoded_id)
    return encoded_id


def encode_file_ref(file_ref: bytes) -> str:
    encoded_ref = base64.urlsafe_b64encode(file_ref).decode().rstrip("=")
    logger.debug("Encoded file reference: %s", encoded_ref)
    return encoded_ref


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    logger.info("Unpacking new file ID: %s", new_file_id)
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    logger.info("Unpacked file_id: %s, file_ref: %s", file_id, file_ref)
    return file_id, file_ref


def generate_batch_id():
    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_part = hashlib.sha256(current_timestamp.encode()).hexdigest()[:10]
    sequence_number = get_latest_batch_sequence() + 1
    batch_id = f"BATCH-{hash_part}-{str(sequence_number).zfill(2)}"
    logger.info("Generated batch ID: %s", batch_id)
    return batch_id


def get_latest_batch_sequence():
    latest_batch = col.find().sort("batch_id", -1).limit(1)
    if latest_batch.count() > 0:
        latest_batch_data = latest_batch[0]
        batch_id = latest_batch_data.get("batch_id", "")
        if batch_id:
            try:
                return int(batch_id.split("-")[-1])
            except ValueError:
                logger.warning("Invalid batch_id format: %s", batch_id)
                return 0
        else:
            logger.warning("Missing batch_id in batch document.")
            return 0
    return 0


async def save_batch_details(batch_id, file_data, batch_name, optional_message=None):
    logger.info("Saving batch db details for batch ID: %s", batch_id)
    batch_details = {
        "batch_id": batch_id,
        "file_data": file_data,
        "batch_name": batch_name,
        "optional_message": optional_message,
        "created_at": datetime.now()
    }
    try:
        col.insert_one(batch_details)
        logger.info("Batch %s successfully saved to database.", batch_id)
        return batch_id
    except Exception as e:
        logger.error("Error saving batch %s: %s", batch_id, str(e))
        return None


async def get_batch_by_id(batch_id):
    logger.info("Fetching batch details for batch ID: %s", batch_id)
    batch_details = col.find_one({"batch_id": batch_id})
    if batch_details:
        logger.info("Batch details found for batch ID: %s", batch_id)
        return batch_details
    else:
        logger.warning("Batch %s not found.", batch_id)
        return None
