import psycopg2
from elasticsearch import Elasticsearch, helpers

# Koneksi ke PostgreSQL
conn = psycopg2.connect(
    dbname="cybercampus", 
    user="user", 
    password="password", 
    host="localhost", 
    port="5432"
)
cursor = conn.cursor()

# Koneksi ke Elastic Search
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Fungsi untuk mengindeks data akademik ke Elastic Search
def index_to_elasticsearch():
    # Query untuk mengambil data mahasiswa yang terdaftar di mata kuliah tertentu
    cursor.execute("SELECT * FROM students WHERE course_id = %s", (101,))  # Misal mata kuliah ID 101
    students = cursor.fetchall()
    
    actions = []
    for student in students:
        action = {
            "_op_type": "index",
            "_index": "students",
            "_id": student[0],  # ID mahasiswa
            "_source": {
                "name": student[1],  # Nama mahasiswa
                "course": student[2],  # Nama mata kuliah
                "semester": student[3],  # Semester
                "attendance": student[4]  # Kehadiran
            }
        }
        actions.append(action)

    # Melakukan bulk indexing ke Elastic Search
    helpers.bulk(es, actions)

# Fungsi untuk melakukan pencarian mahasiswa berdasarkan mata kuliah dan semester
def search_students(query):
    body = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"course": query["course"]}},
                    {"match": {"semester": query["semester"]}}
                ]
            }
        }
    }
    result = es.search(index="students", body=body)
    for hit in result['hits']['hits']:
        print(hit["_source"])

# Mengindeks data mahasiswa ke Elastic Search
index_to_elasticsearch()

# Melakukan pencarian mahasiswa di mata kuliah semester tertentu
search_query = {"course": "Database Systems", "semester": "Fall 2024"}
search_students(search_query)
