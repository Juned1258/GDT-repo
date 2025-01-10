import boto3
import pymysql
import csv
import io

# AWS S3 Client
s3_client = boto3.client('s3')

# RDS Connection Details
RDS_HOST = 'terraform-20250110134420819000000001.cbw0o2oemypy.ap-south-1.rds.amazonaws.com'            
RDS_USER = 'admin'
RDS_PASSWORD = 'juned1234'
RDS_PORT = 3306  # For MySQL, default port is 3306

# S3 Bucket and File Key (path to the CSV file)
S3_BUCKET = 'gdtbucket'
S3_FILE_KEY = 'data.csv'

def lambda_handler(event, context):
    # Read the file from S3
    try:
        s3_response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
        csv_content = s3_response['Body'].read().decode('utf-8')
        
        # Convert CSV content to list of rows
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)

        # Connect to RDS MySQL (no database specified in the connection)
        connection = pymysql.connect(host=RDS_HOST,
                                      user=RDS_USER,
                                      password=RDS_PASSWORD,
                                      port=RDS_PORT)

        with connection.cursor() as cursor:
            # Assuming the first row contains column names, adjust as needed
            column_names = rows[0]
            
            # Create database if not exists (optional, based on your needs)
            create_db_query = f"CREATE DATABASE IF NOT EXISTS test;"  # Replace 'test' with your desired DB name
            cursor.execute(create_db_query)

            # Use the created database
            use_db_query = "USE test;"  # Use your database name
            cursor.execute(use_db_query)

            # Create table dynamically based on the CSV headers (column names)
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS my_table (
                {', '.join([f'`{col_name}` VARCHAR(255)' for col_name in column_names])}
            );
            """
            cursor.execute(create_table_query)
            
            # Insert rows into the table (skip header row)
            insert_query = f"""
            INSERT INTO my_table ({', '.join([f'`{col_name}`' for col_name in column_names])})
            VALUES ({', '.join(['%s'] * len(column_names))});
            """
            for row in rows[1:]:  # Skipping the header row
                cursor.execute(insert_query, row)
            
            connection.commit()

        return {
            'statusCode': 200,
            'body': f'Successfully processed {len(rows)-1} rows from {S3_FILE_KEY}'
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f'Error processing file: {str(e)}'
        }
