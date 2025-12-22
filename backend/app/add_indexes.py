from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Index for user lookup during login
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
)

# Index for job-user relationship
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)"
)

# Index for filtering by status
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)"
)

# Index for searching company names
cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)"
)

conn.commit()
conn.close()

print("Indexes created successfully")
