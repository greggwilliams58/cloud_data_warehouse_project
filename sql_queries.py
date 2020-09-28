import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = ""
user_table_drop = ""
song_table_drop = ""
artist_table_drop = ""
time_table_drop = ""

# CREATE TABLES

staging_events_table_create= ("""CREATE TABLE staging_events (
        artist             nvarchar(100),
        auth               nvarchar(20),
        first_name         nvarchar(50),
        gender             nvarchar(10),
        item_in_session    int,
        last_name          nvarchar(50),
        length             numeric(11,5),
        level              nvarchar(50),
        location           nvarchar(256),
        page               nvarchar(15),
        session_id         int,
        song               nvarchar(256),
        ts                 bigint,
        user_agent         nvarchar(256),
        user_id            int  
        )
""")

staging_songs_table_create = (""" CREATE TABLE staging_songs(
        num_songs         int,
        artist_id         nvarchar(25),
        artist_latitude   numeric(20,8),
        artist_longitude  numeric(20,8),
        artist_location   nvarchar(60),
        artist_name       nvarchar(150),
        song_id           nvarchar(25),
        title             nvarchar(150),
        duration          numeric(10,5),
        year              int
        )
""")

songplay_table_create = ("""CREATE TABLE fact_songplay diststyle auto(
        songplayid       identity(0,1) NOT NULL PRIMARY KEY,
        start_time       datetime,
        user_id          int,
        level            nvarchar(50),
        song_id          nvarchar(25),
        artist_id        nvarchar(25),
        session_id       int,
        location         nvarchar(256),
        user_agent       nvarchar(256),
        )
""")

user_table_create = ("""CREATE TABLE dimt_users diststyle all (
        user_id       int           NOT NULL PRIMARY KEY,
        first_name    nvarchar(50),
        last_name     nvarchar(50),
        gender        nvarchar(10),
        level         nvarchar(50)
        )
""")

song_table_create = ("""CREATE TABLE dimt_songs diststyle all (
        song_id      nvarchar(25) NOT NULL PRIMARY KEY,
        title             nvarchar(150),
        artist_id        nvarchar(25),
        year              int,
        duration          numeric(10,5)
        )
""")

artist_table_create = ("""CREATE TABLE dimt_artists diststyle all (
        artist_id        nvarchar(25) NOT NULL PRIMARY KEY,
        artist_name       nvarchar(150),
        artist_location   nvarchar(60),
        artist_latitude   numeric(20,8),
        artist_longitude  numeric(20,8) 
        )
""")

time_table_create = ("""CREATE TABLE dimt_time diststyle all (
        time_id     identity(0,1) NOT NULL PRIMARY KEY,
        hour        int,
        week        int,
        month       int,
        year        int,
        weekday     boolean)
""")

# STAGING TABLES

staging_events_copy = ("""
""").format()

staging_songs_copy = ("""
""").format()

# FINAL TABLES

songplay_table_insert = ("""
""")

user_table_insert = ("""
""")

song_table_insert = ("""
""")

artist_table_insert = ("""
""")

time_table_insert = ("""
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
