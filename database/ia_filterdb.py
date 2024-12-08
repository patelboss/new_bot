import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import FILE_DB_URI, SEC_FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME, MULTIPLE_DATABASE, USE_CAPTION_FILTER, MAX_B_TN
from utils import get_settings, save_group_settings
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = MongoClient(FILE_DB_URI)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

sec_client = MongoClient(SEC_FILE_DB_URI)
sec_db = sec_client[DATABASE_NAME]
sec_col = sec_db[COLLECTION_NAME]

async def save_file(media):
    """Save file in database"""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    found1 = {'file_name': file_name}
    check = col.find_one(found1)
    if check:
        print(f"{file_name} is already saved.")
        return False, 0
    check2 = sec_col.find_one(found1)
    if check2:
        print(f"{file_name} is already saved.")
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
        found = {'file_id': file_id}
        check = col.find_one(found)
        if check:
            print(f"{file_name} is already saved.")
            return False, 0
        else:
            try:
                sec_col.insert_one(file)
                print(f"{file_name} is successfully saved.")
                return True, 1
            except DuplicateKeyError:      
                print(f"{file_name} is already saved.")
                return False, 0
    else:
        try:
            col.insert_one(file)
            print(f"{file_name} is successfully saved.")
            return True, 1
        except DuplicateKeyError:      
            print(f"{file_name} is already saved.")
            return False, 0

async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
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
    # Slice files according to offset and max results
    if MULTIPLE_DATABASE:
        cursor1.skip(offset).limit(max_results)
        cursor2.skip(offset).limit(max_results)
    else:
        cursor.skip(offset).limit(max_results)
    # Get list of files
    if MULTIPLE_DATABASE:
        files1 = list(cursor1)
        files2 = list(cursor2)
        files = files1 + files2
    else:
        files = list(cursor)

    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, filter=False):
    """For given query return (results, next_offset)"""
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
    
    # Get list of files
    if MULTIPLE_DATABASE:
        files1 = list(cursor1)
        files2 = list(cursor2)
        files = files1 + files2
    else:
        files = list(cursor)
    
    return files, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    filedetails = col.find_one(filter)
    if not filedetails:
        filedetails = sec_col.find_one(filter)
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

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
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
    return file_id, file_ref


from pymongo import UpdateOne
import hashlib
import json
from datetime import datetime

# Function to generate a unique batch ID (e.g., BATCH-XXXXXXXXXX-01)
from pymongo import MongoClient
from datetime import datetime
import hashlib
import logging

# Ensure that MongoDB client and collections are initialized properly
client = MongoClient(FILE_DB_URI)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

logger = logging.getLogger(__name__)

# Function to generate a unique batch ID (e.g., BATCH-XXXXXXXXXX-01)


def generate_batch_id():
    try:
        # Generate a unique timestamp
        current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        logger.debug(f"Generated timestamp for batch ID: {current_timestamp}")

        # Generate a hash part for the batch ID
        hash_part = hashlib.sha256(current_timestamp.encode()).hexdigest()[:10]
        logger.debug(f"Generated hash part for batch ID: {hash_part}")

        # Get the latest sequence number
        sequence_number = get_latest_batch_sequence() + 1
        logger.info(f"Retrieved and incremented sequence number for batch ID: {sequence_number}")

        # Combine to create the batch ID
        batch_id = f"BATCH-{hash_part}-{str(sequence_number).zfill(2)}"
        logger.info(f"Generated batch ID: {batch_id}")

        return batch_id
    except Exception as e:
        logger.error(f"Error generating batch ID: {str(e)}")
        raise  # Re-raise the exception to allow for further handling if needed
# Function to get the latest batch sequence number (for uniqueness)

def get_latest_batch_sequence():
    try:
        logger.info("Attempting to retrieve the latest batch sequence number.")
        
        # Query to find the most recent batch
        latest_batch = col.find().sort("batch_id", -1).limit(1)
        logger.debug("Query executed to find the latest batch.")

        if latest_batch.count() > 0:
            latest_batch_data = latest_batch[0]
            batch_id = latest_batch_data.get("batch_id", "")

            if batch_id:
                logger.info(f"Found latest batch_id: {batch_id}")
                try:
                    # Extract and return the sequence number
                    sequence_number = int(batch_id.split("-")[-1])
                    logger.info(f"Extracted sequence number: {sequence_number}")
                    return sequence_number
                except ValueError:
                    logger.warning(f"Invalid batch_id format encountered: {batch_id}")
                    return 0
            else:
                logger.warning("Batch document found but missing 'batch_id' field.")
                return 0
        else:
            logger.info("No batches found in the collection. Starting with sequence number 0.")
            return 0
    except Exception as e:
        logger.error(f"Error retrieving the latest batch sequence: {str(e)}")
        return 0
# Function to save batch details to the database

async def save_batch_details(batch_id, file_data, batch_name, optional_message=None):
    try:
        # Generate a unique batch ID
        batch_id = generate_batch_id()
        logger.info(f"Generated batch ID: {batch_id}")

        # Prepare batch details
        batch_details = {
            "batch_id": batch_id,
            "file_data": file_data,
            "batch_name": batch_name,
            "optional_message": optional_message,
            "created_at": datetime.now()
        }
        logger.debug(f"Batch details prepared: {batch_details}")

        # Save batch details in the main collection
        col.insert_one(batch_details)
        logger.info(f"Batch {batch_id} saved successfully with name '{batch_name}'")
    except Exception as e:
        # Log the error
        logger.error(f"Error saving batch {batch_id}: {str(e)}")
        raise  # Re-raise the exception for further handling if needed

async def get_batch_by_id(batch_id):
    """
    Retrieve batch details from the database using batch_id.
    
    :param batch_id: The unique ID of the batch to retrieve.
    :return: A dictionary containing batch details if found, otherwise None.
    """
    try:
        logger.info(f"Attempting to retrieve batch with ID: {batch_id}")
        
        # Query the database for the batch
        batch_details = col.find_one({"batch_id": batch_id})
        
        if batch_details:
            logger.info(f"Batch {batch_id} found in the database. Details: {batch_details}")
            return batch_details
        else:
            logger.warning(f"Batch {batch_id} not found in the database.")
            return None
    except PyMongoError as e:
        logger.error(f"Error retrieving batch {batch_id} from the database: {str(e)}")
        return None
