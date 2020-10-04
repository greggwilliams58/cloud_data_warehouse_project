import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

IAM_ROLE      = config.get('IAM_ROLE','ARN')
LOG_DATA      = config.get('S3','LOG_DATA')
LOG_JSON_PATH = config.get('S3','LOG_JSONPATH')
SONG_DATA     = config.get('S3','SONG_DATA')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS fact_songplays"
user_table_drop = "DROP TABLE IF EXISTS dimt_users"
song_table_drop = "DROP TABLE IF EXISTS dimt_songs"
artist_table_drop = "DROP TABLE IF EXISTS dimt_artists"
time_table_drop = "DROP TABLE IF EXISTS dimt_time"

# CREATE TABLES

staging_events_table_create = ("""CREATE TABLE IF NOT EXISTS staging_events (
        artist             nvarchar(500),
        auth               nvarchar(20),
        first_name         nvarchar(50),
        gender             nvarchar(10),
        item_in_session    int,
        last_name          nvarchar(50),
        length             numeric(11,5),
        level              nvarchar(50),
        location           text,
        method             nvarchar(5),
        page               nvarchar(25),
        registration       float,
        session_id         int,
        song               text,
        status             int,
        ts                 bigint,
        user_agent         nvarchar(256),
        user_id            int  
        )
""")

staging_songs_table_create = (""" CREATE TABLE IF NOT EXISTS staging_songs(
        num_songs         int,
        artist_id         nvarchar(25),
        artist_latitude   numeric(20,8),
        artist_longitude  numeric(20,8),
        artist_location   text,
        artist_name       nvarchar(500),
        song_id           nvarchar(25),
        title             nvarchar(256),
        duration          numeric(10,5),
        year              int
        )
""")

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS fact_songplays (
        songplayid       int        IDENTITY(0,1) PRIMARY KEY NOT NULL,
        start_time       datetime   NOT NULL,
        user_id          int        NOT NULL ,
        level            nvarchar(50),
        song_id          nvarchar(25),
        artist_id        nvarchar(25),
        session_id       int,
        location         nvarchar(256),
        user_agent       nvarchar(256)
        )
        diststyle auto;
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS dimt_users  (
        user_id            int  NOT NULL PRIMARY KEY,
        user_first_name    nvarchar(50),
        user_last_name     nvarchar(50),
        gender             nvarchar(10),
        level              nvarchar(50)
        )
        diststyle all;
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS dimt_songs (
        song_id      nvarchar(25) NOT NULL PRIMARY KEY,
        title        text,
        artist_id    nvarchar(25),
        year         int,
        duration     numeric(11,5)
        )
        diststyle all;
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS dimt_artists (
        artist_id         nvarchar(25) NOT NULL PRIMARY KEY,
        artist_name       nvarchar(500),
        artist_location   text,
        artist_latitude   numeric(20,8),
        artist_longitude  numeric(20,8) 
        )
        diststyle all;
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS dimt_time (
        time_id     int        IDENTITY(0,1) PRIMARY KEY NOT NULL,
        start_time  datetime,
        hour        int,
        week        int,
        month       int,
        year        int,
        weekday     int
        )
        diststyle all;
""")

# STAGING TABLES

staging_events_copy = ("""COPY staging_events FROM {}
                          credentials 'aws_iam_role={}'
                          region 'us-west-2'
                          format as json {};
                          """).format(LOG_DATA,IAM_ROLE,LOG_JSON_PATH)

staging_songs_copy = ("""COPY staging_songs FROM {}
                        credentials 'aws_iam_role={}'
                        region 'us-west-2'
                        json 'auto';
                        """).format(SONG_DATA,IAM_ROLE)


# FINAL TABLES
songplay_table_insert = ("""INSERT INTO                                   fact_songplays(start_time,user_id,level,song_id,artist_id,session_id,location,user_agent)
SELECT distinct TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, user_id ,level,song_id,artist_id,session_id,location,user_agent
FROM staging_events AS events
JOIN staging_songs AS songs
ON (events.artist = songs.artist_name)
AND (events.song = songs.title)
AND (events.length = songs.duration)
WHERE page = 'NextSong'
                             
""")

user_table_insert = ("""INSERT INTO dimt_users (user_id,user_first_name,user_last_name,gender,level)
                        SELECT distinct user_id ,first_name,last_name,gender,level
                        FROM staging_events WHERE user_id IS NOT NULL
""")

song_table_insert = ("""INSERT INTO dimt_songs(song_id,title,artist_id,year, duration)
                        SELECT distinct song_id, title, artist_id, year,duration
                        FROM staging_songs
""")

artist_table_insert = ("""INSERT INTO dimt_artists (artist_id, artist_name,artist_location,artist_latitude,artist_longitude)
                           SELECT DISTINCT artist_id,artist_name,artist_location,artist_latitude ,artist_longitude
                           FROM staging_songs WHERE artist_id IS NOT NULL
""")

time_table_insert = ("""INSERT INTO dimt_time (start_time,hour,week, month,year,weekday)
                     (
                     SELECT T.start_time,
                     EXTRACT (HOUR FROM T.start_time),
                     EXTRACT (WEEK FROM T.start_time),
                     EXTRACT (MONTH FROM T.start_time),
                     EXTRACT (YEAR FROM T.start_time),
                     EXTRACT (WEEKDAY FROM T.start_time)                     
                     FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' as start_time FROM staging_events)
                         AS T
                         )
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]

drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]

copy_table_queries = [staging_events_copy, staging_songs_copy]

insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
