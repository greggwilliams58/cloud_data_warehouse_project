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
#### Most popular song title
    SELECT TOP 10 count(events.song_id), songs.title
    FROM fact_songplays as events
    JOIN dimt_songs  as songs
    ON (events.song_id = songs.song_id)
    GROUP BY songs.title
    order by count(events.song_id) DESC

#### Results
    count,title
    37,You're The One
    9,I CAN'T GET STARTED
    9,Catch You Baby (Steve Pitron & Max Sanna Radio Edit)
    8,Nothin' On You [feat. Bruno Mars] (Album Version)
    6,Hey Daddy (Daddy's Home)
    5,Make Her Say
    5,Up Up & Away
    4,Unwell (Album Version)
    4,Mr. Jones
    4,Supermassive Black Hole (Album Version)
    
#### Which gender listens to the most songs?
    SELECT TOP 10 count(events.user_id), users.gender
    FROM fact_songplays as events
    JOIN dimt_users  as users
    ON (events.user_id = users.user_id)
    GROUP BY users.gender
    ORDER BY count(events.user_id), users.gender ASC
    
#### Results
    count,gender
    94,M
    225,F

#### What songs were played in November 2018
    SELECT count(S.song_id), A.artist_name, S.title
    from fact_songplays as events
    JOIN dimt_time AS T ON (events.start_time = T.start_time)
    JOIN dimt_artists AS A ON (events.artist_id = A.artist_id)
    JOIN dimt_songs AS S ON (events.song_id = S.song_id)
    where EXTRACT (YEAR FROM t.start_time) = 2018
    AND EXTRACT (MONTH FROM t.start_time )= 11
    GROUP BY A.artist_name, S.title
    order by count(S.song_id) DESC

#### Results
    count,artist_name,title
    37,Dwight Yoakam,You're The One
    9,Ron Carter,I CAN'T GET STARTED
    9,Lonnie Gordon,Catch You Baby (Steve Pitron & Max Sanna Radio Edit)
    8,B.o.B,Nothin' On You [feat. Bruno Mars] (Album Version)
    6,Usher featuring Jermaine Dupri,Hey Daddy (Daddy's Home)
    5,Kid Cudi,Up Up & Away
    5,Kid Cudi,Make Her Say
    4,Counting Crows,Mr. Jones
    4,Muse,Supermassive Black Hole (Album Version)
    4,matchbox twenty,Unwell (Album Version)
    3,Metallica,Fade To Black
    3,Linkin Park,Given Up (Album Version)
    3,Fisher,Rianna
    3,Black Eyed Peas / Les Nubians / Mos Def,Let's Get It Started
    3,Richard Hawley And Death Ramps_ Arctic Monkeys,From The Ritz To The Rubble
    2,Richard Hawley And Death Ramps_ Arctic Monkeys,Fake Tales Of San Francisco
    2,The Verve,Bitter Sweet Symphony
    2,The Smiths,Girlfriend In A Coma
    2,Duncan Dhu,No Puedo Evitar (Pensar En Ti)
    2,Josh Turner,What It Ain't
    2,Coldplay,Don't Panic
    2,38 Special,Caught Up In You
    2,New Radicals,You Get What You Give
    2,The Smiths,The Boy With The Thorn In His Side
    2,The Rolling Stones,Angie (1993 Digital Remaster)
    2,Taylor Swift,The Way I Loved You
    2,Paramore,Emergency (Album Version)
    2,Ashanti,VooDoo
    2,The Cardigans,Lovefool
    2,Alice In Chains,God Smack
    2,Slim Dusty,Long Black Road
    2,Sparklehorse,Marigold
    2,Jack Johnson,Monsoon
    2,Emmy The Great,Mia
    2,David Arkenstone,Waterfall (Spirit Of The Rainforest Album Version)
    1,Dash Berlin,Till The Sky Falls Down
    1,India.Arie,Beautiful Flower
    1,Steve Miller Band,The Joker
    1,Bobby Goldsboro,Honey
    1,Ghostland Observatory,Club Soda (Album)
    1,Marea,Marea (version acustica)
    1,Whitesnake,Fool For Your Loving
    1,Tomcraft,Loneliness
    1,Mayer Hawthorne,Shiny & New
    1,Brand New Disaster,At Least It's Raining
    1,Pearl Jam,Not For You
    1,De-Phazz,Astrud Astronette
    1,Placebo,English Summer Rain
    1,Coldplay,One I Love
    1,Los Rodriguez,Enganchate Conmigo
