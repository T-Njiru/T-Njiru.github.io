import mysql.connector

def get_database_connection():
    """Connects to the MySQL database and returns the connection object."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Planogram_Adherence"
        )
        return conn
    except mysql.connector.Error as err:
        print("Error: Could not connect to database:", err)
        return None

def get_image_path(image_id):
    """
    Fetches the image path from the database based on the image ID.

    :param image_id: ID of the image in the database.
    :return: Image file path (string) or None if not found.
    """
    conn = get_database_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor()
    query = "SELECT image_path FROM images_table WHERE id = %s"  # Update table/column name if needed
    cursor.execute(query, (image_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Return image path from database
    else:
        print(f"Error: No image found for ID {image_id}")
        return None
