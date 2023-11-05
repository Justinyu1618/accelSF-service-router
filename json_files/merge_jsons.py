import json

json_files = ['pg1.json', 'pg2.json', 'pg3.json', 'pg4.json', 'pg5.json', 'pg6.json', 'pg7.json', 
'pg8.json', 'pg9.json', 'pg10.json', 'pg11.json', 'pg12.json', 'pg13.json', 'pg14.json', 'pg15.json', 'pg16.json',
'pg17.json', 'pg18.json', 'pg19.json', 'pg20.json', 'pg21.json', 'pg22.json', 'pg23.json', 'pg24.json', 
'post-25.json', 'post-26.json', 'post-27.json', 'post-28.json', 'post-29.json', 'post-30.json', 'post-31.json',
'post-32.json', 'post-33.json', 'post-34.json', 'post-35.json', 'post-36.json', 'post-36.json', 'post-37.json',
'post-38.json', 'post-39.json', 'post-40.json', 'post-41.json', 'post-42.json', 'post-43.json', 'post-44.json', 
'post-45.json', 'post-46.json', 'post-47.json', 'post-48.json', 'post-49.json']

merged_data = []
unique_ids = set()

with open('pg0.json', "r") as f:
    merged_data.append(json.load(f))

for pg_file in json_files: 
    with open(pg_file, "r") as f:
        page = json.load(f)
        hits = page["results"][0]["hits"]
        for hit in hits: 
            id = hit["id"]
            if id not in unique_ids:
                unique_ids.add(id)
                merged_data[0]["results"][0]["hits"].append(hit)
print(unique_ids)

with open("combined_pgs.json", "w") as f:
    json.dump(merged_data, f, indent=4)