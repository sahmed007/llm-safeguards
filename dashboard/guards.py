import os
import openai

from dotenv import load_dotenv
from guardrails import Guard
from guardrails.hub import (
    ExcludeSqlPredicates,
    ValidSQL,
    SqlColumnPresence,
)

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

formatted_schema = """
applicants
    - first_name (text)
    - last_name (text)
    - email (text)
    - phone (text)
    - education (text)
    - company (text)
    - years_of_experience (text)
    - work_experience (text)
    - skills (text)
"""

system_prompt = (
    f"You are a professional sqlite3 query writer. The user will provide you "
    f"with a natural language query and your job is to convert that to SQL based "
    f"on the schema of the applicants database: {formatted_schema}. Think step-by-step "
    f"through the process to make sure the query makes sense and includes columns "
    f"that actually exist in each table. Only output the SQL query and make sure "
    f"to add ';' at the end so the query can be run. Your output will be used in "
    f"a function to query a database so it is important not to return another "
    f"other text if your response. Do not include any explanation."
)

guards = Guard().use_many(
    ExcludeSqlPredicates(
        predicates=["Drop"], on_fail="excluded_sql_predicate_exception"
    ),
    SqlColumnPresence(
        cols=[
            "first_name",
            "last_name",
            "email",
            "phone",
            "education",
            "company",
            "years_of_experience",
            "work_experience",
            "skills",
        ],
        on_fail="sql_column_presence_exception",
    ),
    ValidSQL(on_fail="invalid_sql_exception"),
)

try:
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "How many applicants do I have for this role?"},
        ],
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(e)
