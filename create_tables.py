import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    """
    This function loops through a list of queries to drop tables from the dw
    
    Parameters:
    cur       a cursor object to interac with the dw
    conn      a connection object for the dw cluster
    
    Returns
    NULL, but tables are dropped
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    This function loops through a list of queries to create tables from the dw
    
    Parameters:
    cur       a cursor object to interac with the dw
    conn      a connection object for the dw cluster
    
    Returns
    NULL, but tables are dropped
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    This main function extracts the configuration information from the dwh.cfg file, then connects to the redshift cluster then the 
    data warehouse (creating the connection and cursor objects), calls the functions above to drop and create tables as needed.
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

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()