from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import duckdb

app = FastAPI()

DATA_URL = 'hf://datasets/TfqDeadlox636/icrm-hitek-fulldb/*.parquet'

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Search API</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 25px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; }
            input { width: 85%; padding: 12px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 16px; outline: none; }
            button { background: #3b82f6; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-size: 16px; cursor: pointer; width: 92%; }
            button:hover { background: #2563eb; }
            #result { margin-top: 20px; text-align: left; background: #0f172a; padding: 12px; border-radius: 6px; font-size: 13px; word-break: break-all; max-height: 250px; overflow-y: auto; border: 1px solid #334155; }
            pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Quick Search</h2>
            <input type="text" id="phone" placeholder="Enter Phone Number" onkeydown="handleEnter(event)">
            <br>
            <button onclick="searchData()">Search</button>
            <div id="result">Results will appear here...</div>
        </div>
        <script>
            function handleEnter(event) {
                if (event.key === 'Enter') {
                    searchData();
                }
            }

            async function searchData() {
                const phone = document.getElementById('phone').value.trim();
                const resultDiv = document.getElementById('result');
                if(!phone) {
                    resultDiv.innerHTML = "Please enter a phone number.";
                    return;
                }
                
                resultDiv.innerHTML = "Searching... (Note: Free server may take 30s to wake up if idle)";
                
                try {
                    const response = await fetch('/search/' + encodeURIComponent(phone));
                    const data = await response.json();
                    if(response.ok) {
                        resultDiv.innerHTML = "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
                    } else {
                        resultDiv.innerHTML = data.detail || "Not found";
                    }
                } catch(err) {
                    resultDiv.innerHTML = "Error connecting to server. Please try again after 30 seconds.";
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/search/{user_number}")
def search_number(user_number: str):
    try:
        # CAST aur LIKE ka use kiya hai taaki partial match ho sake aur format issue na aaye
        query = f"SELECT * FROM read_parquet('{DATA_URL}') WHERE CAST(PhoneNumber AS VARCHAR) LIKE '%{user_number}%'"
        result = duckdb.query(query).to_df()
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Number nahi mila")
        
        return result.to_dict(orient="records")[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
