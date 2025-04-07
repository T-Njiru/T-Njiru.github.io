import mysql.connector
from mysql.connector import pooling
import logging
import time
from config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("database")

# Connection pool for better performance
connection_pool = None

def initialize_connection_pool():
    """Initialize the database connection pool."""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="planogram_pool",
            pool_size=DB_CONFIG['pool_size'],
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            ssl_disabled=DB_CONFIG['ssl_disabled']
        )
        logger.info("Connection pool created successfully")
    except mysql.connector.Error as err:
        logger.error(f"Error creating connection pool: {err}")
        raise

def get_connection(max_retries=3, retry_delay=1):
    """Get a connection from the pool with retry logic.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        mysql.connector.connection: Database connection
        
    Raises:
        mysql.connector.Error: If connection cannot be established after retries
    """
    global connection_pool
    
    # Initialize pool if not already done
    if connection_pool is None:
        initialize_connection_pool()
    
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            # Get connection from pool
            conn = connection_pool.get_connection()
            return conn
        except mysql.connector.Error as err:
            last_error = err
            logger.warning(f"Connection attempt {retries+1} failed: {err}")
            retries += 1
            if retries < max_retries:
                time.sleep(retry_delay)
    
    # If we get here, all retries failed
    logger.error(f"Failed to get database connection after {max_retries} attempts")
    
    # Fallback to direct connection
    try:
        logger.info("Attempting direct connection as fallback")
        return mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )
    except mysql.connector.Error as err:
        logger.critical(f"Direct connection fallback also failed: {err}")
        raise last_error

def execute_query(query, params=None, fetch=True, commit=False):
    """Execute a database query with proper connection handling.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch (bool): Whether to fetch results
        commit (bool): Whether to commit the transaction
        
    Returns:
        list: Query results if fetch=True, otherwise None
        
    Raises:
        Exception: If query execution fails
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        result = None
        if fetch:
            result = cursor.fetchall()
        if commit:
            conn.commit()
            
        return result
    except Exception as e:
        if conn and commit:
            logger.error(f"Rolling back transaction due to error: {e}")
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_image_path(image_id):
    """Get the file path for an image by its ID.
    
    Args:
        image_id (int): The ID of the image
        
    Returns:
        str: The file path of the image or None if not found
    """
    try:
        result = execute_query(
            "SELECT filepath FROM images WHERE image_id = %s", 
            (image_id,)
        )
        return result[0]["filepath"] if result else None
    except Exception as e:
        logger.error(f"Error retrieving image path for ID {image_id}: {e}")
        return None

def save_image_data(filename, filepath):
    """Save image metadata to the database.
    
    Args:
        filename (str): Original filename of the image
        filepath (str): Path where the image is stored
        
    Returns:
        int: The ID of the inserted image or None on failure
    """
    try:
        execute_query(
            "INSERT INTO images (filename, filepath, uploaded_at) VALUES (%s, %s, NOW())",
            (filename, filepath),
            fetch=False,
            commit=True
        )
        # Get the last inserted ID
        result = execute_query("SELECT LAST_INSERT_ID() as id")
        return result[0]["id"] if result else None
    except Exception as e:
        logger.error(f"Error saving image data: {e}")
        return None
