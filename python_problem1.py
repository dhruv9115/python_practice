"""
Question 1: Parse and Summarize Log Files

Problem:
Write a Python script that reads a server log file, extracts errors, and outputs a summary of errors grouped by error type and how many times each error occurred. Log lines follow this format:

```log
2024-09-18 12:35:22 ERROR ConnectionTimeout: Connection to database failed
2024-09-18 12:36:01 INFO Connection restored
2024-09-18 12:36:55 ERROR IOError: Unable to read file /etc/config.cfg
```
Requirements:
1. Parse the log file and find all lines that contain the word "ERROR."
2. Group errors by their error type (e.g., ConnectionTimeout, IOError) and count their occurrences.
3. Store the summary on to a database (sqlight setup function provided).
4. Output the summary as a dictionary
"""

import sqlite3

SQLITE_DATABASE_PATH = 'server.db'
LOG_FILE_PATH = 'server.log'


def _setup_database(database_path: str) -> None:
    """
    Set up the SQLite database for storing error summaries.
    Connect to the SQLite database (or create it if it doesn't exist)

    :param database_path: Path to the SQLite database.
    :return: None
    """

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP,
            error_type VARCHAR(250),
            count INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def save_to_database(summary: dict[str, int], database_path: str) -> None:
    """
    Update the error_summary table with:
    date = summary[key][0]
    error_type = key
    count = summary[key][1]

    :param summary: summary is a dict["error_name": ["time_stamp", error_count_in_log]]
    :return: None
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    for key in summary:
        cursor.execute("""
        INSERT INTO error_summary (date, error_type, count) VALUES
            (?,?,?)
        """, (summary[key][0], key, summary[key][1]))

    conn.commit()
    conn.close()


def summarise_errors(log_file_path: str) -> dict[str, int] | dict[None, None]:
    """
    This function parses through the log file and outputs the error summary
    :param log_file_path: Path to the log file
    :return: summary in format dict["error_name": ["time_stamp", error_count_in_log]]
    """
    error_dict = dict()
    with open(log_file_path, "r") as inputfile:
        for line in inputfile:
            if "ERROR" in line:
                error_name = get_error_name(line)
                time_stamp = get_time_stamp(line)
                print(f"Error Name {error_name}")
                if error_name not in error_dict:
                    error_dict[error_name] = ["", 0]
                error_dict[error_name][0] = time_stamp
                error_dict[error_name][1] += 1
    print(error_dict)
    return error_dict


def get_error_name(line):
    """
    This function gets the error name for eg. ConnectionTimeout, IOError etc.
    :param line: Line in the log file
    :return: error name
    """
    error = line.split("ERROR")
    error_split = error[1].split(":")
    error_nm = error_split[0].replace(" ", "")
    return error_nm


def get_time_stamp(line):
    """
    This function gets the time stamp of the error
    :param line: Line in the log file
    :return: time stamp
    """
    error = line.split("ERROR")
    time_stamp = error[0].strip()
    return time_stamp


if __name__ == "__main__":
    _setup_database('server.db')
    summary = summarise_errors('server.log')
    save_to_database(summary, 'server.db')
