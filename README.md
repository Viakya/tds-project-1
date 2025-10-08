uvicorn app.main:app --reload


csv64=$(base64 -w 0 data.csv)
img1_64=$(base64 -w 0 photo1.png)
img2_64=$(base64 -w 0 photo2.png)

jq --arg csv "$csv64" \
   --arg img1 "$img1_64" \
   --arg img2 "$img2_64" \
   '.attachments = [
      {"name": "data.csv", "url": ("data:text/csv;base64," + $csv)},
      {"name": "photo1.png", "url": ("data:image/png;base64," + $img1)},
      {"name": "photo2.png", "url": ("data:image/png;base64," + $img2)}
    ]' request.json > final_request.json


curl -X POST http://127.0.0.1:8000/api-endpoint \
     -H "Content-Type: application/json" \
     -d @final_request.json
