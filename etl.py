import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    This function loops through a list of queries to insert data into the staging tables
    staging_events and staging_songs
    
    Parameters:
    cur       a cursor object to interac with the dw
    conn      a connection object for the dw cluster
    
    Returns
    NULL, but inserts data into the staging tables
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    This function loops through a list of queries to insert data into the fact and dim tables
    
    Parameters:
    cur       a cursor object to interac with the dw
    conn      a connection object for the dw cluster
    
    Returns
    NULL, but inserts data into the dw tables
    
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()
    """


def main():
    """
    This main function extracts the configuration information from the dwh.cfg file, then connects to the redshift cluster then the 
    data warehouse (creating the connection and cursor objects), calls the functions above to load data into the staging and dw tables.
    The connection to the cluster and dwh is then closed.
    
    Parameters:
    NONE
    
    Returns:
    NULL, but all data is returned.
    
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()