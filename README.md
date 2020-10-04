# Cloud Data Warehouse Project

##1. Purpose of this database
This database has been designed to allow Sparkify to place their data onto a cloud based Redshift data warehouse for later subsequent data analysis.  Their data was prevously held in the format of JSON files on S3 buckets, with separate folders for user_activity and song information.  The data has been moved to the cloud to take advantage of the cloud's scaleability, reduction in up-front costs of using on-premises servers and to make use of other AWS analytical services in due course 

##2. How to execute this code
Go to a terminal session and type "python create_tables.py"  This will be a brief execution as the script calls the drop_tables function to drop a set of tables defined by the list in the sql_queries.py file.  The create_tables function is then used to create the necessary tables for the rest of the project.

Create a redshift cluster in the normal manner, either from the AWS front page or a IaC script.

Once the cluster is up and running with the necessary permissions to access the s3 service, then type "etl.py" in the terminal.  This will copy the relevant data from the s3 buckets into the staging_tables, which are then inserted to the fact and dimt tables as needed.

##3. Files in project
    1. create_tables.py - Python script to drop and create tables in dwh database, held on a redshift cluster
    2. sql_queries.py - Python script holding the various SQL queries used by create_tables.py and elt.py
    3. etl.py - Python script to run the ETL process
    4. dwh.cfg - a configuration file for connecting to Redshift cluster and S3 buckets
    5. dw_schema.jpg - a diagram of the dw_schema
    6. staging_tables.jog - a diagrame of the staging tables and their implied relationship
    7, READ_ME - this document which documents this project.

##4. Project Design
###    1. Database Schema Design
Two staging tables have been created, which are exact copies of the data sourced from the json files in the s3 buckets.  The purpose of these tables is to provide an initial landing point for the data within the redshift database.  This 'staging table' allows the raw data to be examined easily for data quality and consistency prior to any subsequent transformations.  The placing of the raw data within the same data warehouse in different tables allows for a relatively quick and simple set of transformations to be done through SQL as the data is inserted into the relevant tables (eg, changing the milliseconds bigint values  'staging_songs.ts' into a timestamp value in 'dimt_time.start_time')

I have attempted to give nvarchar fields a character limit in order to save storage space as the costs of Redshift storage are proportional to the amount of data being stored.  WHere I have run into larger than expected field sizes I have instead defaulted to text datatype (functionally equivalent to nvarchar(265)).

Regarding the final DW tables, a classical star schema has been adopted with the various data fields sorted into 'facts' (numerical measures of activity) and 'dimension' (items which describe features of the measures).  The prefixes 'dimt' and 'fact' have been used to help identify which tables are which.  The relatively small dim tables have been given a distribution strategy of 'all' so all nodes can access them without shuffling.  The larger fact table has been given a automatic distribution strategy as I do not know the data well enough to assess what the best partitioning strategy would be.

The layout of the schema can be seen here
![The standard schema](/dw_schema.jpg)

The relationships of the staging tables can be seen here
![The staging tables](/staging_tables.jpg)


###    2. ETL Pipeline Design
The raw JSON files are extracted from their S3 buckets using a copy command and are inserted to the staging tables staging_songs and staging_events.  This is the 'Extraction' step of the ETL process.  No attempt at transformation is used at this stage.  This is so that the raw-ist form of the data can be inspected from the staging tables to assess it's quality (eg, any nulls, outliers or unexpected values)

For the 'Transform' and 'Load' part of the ETL process, SQL INSERT statments are then used to insert the data into the relevant table and make any necessary transformations.  One example is changing the milliseconds bigint values of 'staging_songs.ts' into a timestamp value in 'dimt_time.start_time'.  Distinct clauses were also used on the dimt tables to prevent duplicate items being inserted into the table.  

The fact_songplays table was the most complex to populate as it draws data from both staging tables and required a compound key of song_title, artists and song_duration as a join condition.  There was also the requirement to filter for rows where page = 'Next Song'

The dimt_time table was based on a sub_query which converted the fact_songplays.ts into a timestamp value which then had the various time elements extracted from it and then inserted into the dimt_time table.

The dimt_users and dimt_artist tables had failures due to NULL values in the user_id and artist_id fields.  On grounds of data quality, these rows have been omitted with a "WHERE artist_id/user_id IS NOT NULL" clause in the INSERT sub-query.  It might be useful to run queries on these tables to see how many rows have NULL values for these fields to assess the degree to which data is missing.

All other tables were relatively straightforward copying of a sub-set of fields from one staging table into a dimt_table.  I did consider using a CASE expression to convert the weekday value to a boolean, True for days 1-5 and FALSE for days 0 and 6, but decided against it as the users may want to look for patterns in specific weekdays.


###    3. Example queries and results of song play analysis
