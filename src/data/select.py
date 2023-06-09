from data.access import connection
from utils.watch import logger


# Log Emoji: 🗄️🔍


def execute_select(query, params=None, fetchone=True):
    # Connect to the database
    conn = connection()
    conn.open()
    # logger.debug("🗄️🔍 Database connection opened")

    # Create a cursor
    cur = conn.conn.cursor()

    # Execute the query
    cur.execute(query, params)
    conn.conn.commit()
    logger.info("🗄️✏️🟢 Query executed and committed")
    # logger.debug(f"🗄️🔍 Executed select query: {query}")
    #   logger.debug(f"🗄️🔍 Query parameters: {params}")

    # Fetch the results if requested
    result = None
    if fetchone:
        result = cur.fetchone() if cur.rowcount > 0 else None
    else:
        result = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()
    logger.debug("🗄️🔍 Cursor and connection closed")

    return result


# Queries
"""
Temp holding for axe sql
WITH prioritized_urls AS (
    SELECT t.id, t.url
    FROM targets.urls t
    INNER JOIN results.scan_uppies s ON t.id = s.url_id
    AND (s.content_type ILIKE 'text/html'
        OR s.content_type IS NULL
        )
    WHERE t.active_main IS TRUE
        AND t.is_objective IS TRUE
        AND (t.uppies_code BETWEEN 100
            AND 299 OR t.uppies_code IS NULL)
        AND (t.scanned_at_axe > now() - interval '7 days'
        OR t.scanned_at_axe IS NULL)
        AND (t.queued_at_axe IS NULL
            OR t.queued_at_axe < now() - interval '1 hour')
    ORDER BY t.queued_at_axe ASC NULLS FIRST
    LIMIT %s
)
SELECT * FROM prioritized_urls
ORDER BY RANDOM()
LIMIT %s;
"""


# Select Axe URL
def get_axe_url(batch_size=10):
    select_query = """
        WITH prioritized_urls AS (
            SELECT t.id, t.url
            FROM targets.urls t
            WHERE t.active_main IS TRUE
                AND t.is_objective IS TRUE
                AND t.active_scan_axe IS TRUE
                AND t.errored is not TRUE
                AND (t.uppies_code BETWEEN 100
                    AND 299 OR t.uppies_code IS NULL)
                AND (t.scanned_at_axe > now() - interval '7 days'
                OR t.scanned_at_axe IS NULL)
                AND (t.queued_at_axe IS NULL
                    OR t.queued_at_axe < now() - interval '2 hour')
            ORDER BY t.queued_at_axe ASC NULLS FIRST
            LIMIT %s
        )
        SELECT * FROM prioritized_urls
        ORDER BY RANDOM()
        LIMIT %s;
    """
    limit = batch_size * 10
    result = execute_select(
        select_query, (limit, batch_size), fetchone=False)
    logger.debug(f'Selected URLs: {result}')
    return result


# Get next Uppies URL
def get_uppies_url(batch_size=10):
    select_query = """
        WITH prioritized_urls AS (
            SELECT t.id, t.url
            FROM targets.urls t
            WHERE t.active_main IS TRUE
                AND t.is_objective IS TRUE
                AND t.active_scan_uppies IS TRUE
                AND (t.queued_at_uppies IS NULL
                    OR t.queued_at_uppies < now() - interval '2 hour')
            ORDER BY t.queued_at_uppies ASC NULLS FIRST
            LIMIT %s
        )
        SELECT * FROM prioritized_urls
        ORDER BY RANDOM()
        LIMIT %s;
    """
    limit = batch_size * 10
    result = execute_select(
        select_query, (limit, batch_size), fetchone=False)
    logger.debug(f'Selected URLs: {result}')
    return result


# Get next CRAWL url
def get_crawl_url(batch_size):
    select_query = """
        WITH prioritized_urls AS (
            SELECT t.id, t.url
            FROM targets.urls t
            WHERE t.active_main IS TRUE
                AND t.is_objective IS TRUE
                AND t.errored is not TRUE
                AND t.active_crawler IS TRUE
                AND (t.scanned_at_uppies > now() - interval '7 days'
                OR t.scanned_at_uppies IS NULL)
                AND (t.queued_at_crawler IS NULL
                    OR t.queued_at_crawler < now() - interval '2 hour')
            ORDER BY t.queued_at_crawler ASC NULLS FIRST
            LIMIT %s
        )
        SELECT * FROM prioritized_urls
        ORDER BY RANDOM()
        LIMIT %s;
    """
    limit = batch_size * 10
    result = execute_select(
        select_query, (limit, batch_size), fetchone=False)
    logger.debug(f'Selected URLs: {result}')
    return result
