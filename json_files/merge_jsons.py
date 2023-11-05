import json

json_files = ['pg0.json', 'pg1.json', 'pg2.json', 'pg3.json', 'pg4.json', 'pg5.json', 'pg6.json', 'pg7.json', 
'pg8.json', 'pg9.json', 'pg10.json', 'pg11.json', 'pg12.json', 'pg13.json', 'pg14.json', 'pg15.json', 'pg16.json',
'pg17.json', 'pg18.json', 'pg19.json', 'pg20.json', 'pg21.json', 'pg22.json', 'pg23.json', 'pg24.json']

python_objects = []

for pg_file in json_files: 
    with open(pg_file, "r") as f:
        python_objects.append(json.load(f))

with open("combined_pgs.json", "w") as f:
    json.dump(python_objects, f, indent=4)