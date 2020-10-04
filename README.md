# Cloud Data Warehouse Project

##1. Purpose of this database
This database has been designed to allow Sparkify to place their data onto a cloud based Redshift data warehouse for later subsequent data analysis.  Their data was prevously held in the format of JSON files on S3 buckets, with separate folders for user_activity and song information.  The data has been moved to the cloud to take advantage of the cloud's scaleability, reduction in up-front costs of using on-premises servers and to make use of other AWS analytical services in due course 

##2. Project Design
###    1. Database Schema Design
Two staging tables have been created, which are exact copies of the data sourced from the json files in the s3 buckets.  The purpose of these tables is to provide an initial landing point for the data within the redshift database.  This 'staging table' allows the raw data to be examined easily for data quality and consistency prior to any subsequent transformations.  The placing of the raw data within the same data warehouse in different tables allows for a relatively quick and simple set of transformations to be done through SQL as the data is inserted into the relevant tables (eg, changing the milliseconds bigint values  'staging_songs.ts' into a timestamp value in 'dimt_time.start_time') This is the 'Extraction' part of the ETL process.

For the 'Transform' and 'Load' part of the process, SQL INSERT statments are then used to insert the data into the relevant table and make any necessary transformations.  Changing the milliseconds bigint values of 'staging_songs.ts' into a timestamp value in 'dimt_time.start_time')

Regarding the final DW tables, a classical star schema has been adopted with the various data fields sorted into 'facts' (numerical measures of activity) and 'dimension' (items which describe features of the measures).  The prefixes 'dimt' and 'fact' have been used to help identify which tables are which.  The relatively small dim tables have been given a distribution strategy of 'all' so all nodes can access them without shuffling.  The larger fact table has been given a automatic distribution strategy as I do not know the data well enough to assess what the best partitioning strategy would be.


###    2. ETL Pipeline Design
The ETL Pipeline is designed to use SQL INSERT statements .


###3. Example queries and results of song play analysis
