from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import duckdb

app = FastAPI()

DATA_URL = 'hf://datasets/TfqDeadlox636/icrm-hitek-fulldb/*.parquet'

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cyber Search Hub | High-Speed Query Terminal</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-gradient: radial-gradient(circle at 50% 10%, #1e1b4b 0%, #0f172a 60%, #020617 100%);
                --card-bg: rgba(30, 41, 59, 0.7);
                --border-color: rgba(99, 102, 241, 0.2);
                --accent-color: #6366f1;
                --accent-hover: #4f46e5;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --success: #10b981;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: 'Inter', sans-serif;
                background: var(--bg-gradient);
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                width: 100%;
                max-width: 540px;
                background: var(--card-bg);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--border-color);
                border-radius: 20px;
                padding: 35px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 50px rgba(99, 102, 241, 0.1);
                animation: fadeIn 0.6s ease-out;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .header {
                text-align: center;
                margin-bottom: 25px;
            }
            .header h1 {
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.5px;
                background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 6px;
            }
            .header p {
                color: var(--text-muted);
                font-size: 13px;
            }

            .search-box-wrapper {
                position: relative;
                margin-bottom: 20px;
            }

            input {
                width: 100%;
                padding: 14px 18px;
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid #334155;
                border-radius: 12px;
                color: white;
                font-size: 15px;
                font-family: 'Inter', sans-serif;
                outline: none;
                transition: all 0.3s ease;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
            }

            input:focus {
                border-color: var(--accent-color);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), inset 0 2px 4px rgba(0,0,0,0.3);
            }

            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, var(--accent-color), var(--accent-hover));
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            }

            button:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
            }

            button:active {
                transform: translateY(1px);
            }

            #result-container {
                margin-top: 25px;
                display: none;
                animation: slideUp 0.4s ease-out;
            }

            @keyframes slideUp {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                font-size: 12px;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .copy-btn {
                background: transparent;
                border: 1px solid #475569;
                color: var(--text-muted);
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                cursor: pointer;
                width: auto;
                box-shadow: none;
                transition: all 0.2s;
            }

            .copy-btn:hover {
                background: #334155;
                color: white;
                transform: none;
                box-shadow: none;
            }

            pre {
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid #334155;
                padding: 16px;
                border-radius: 12px;
                font-family: 'Fira Code', monospace;
                font-size: 13px;
                color: #38bdf8;
                max-height: 280px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
                box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
            }

            .status-msg {
                text-align: center;
                margin-top: 20px;
                font-size: 13px;
                color: var(--text-muted);
            }

            .error-box {
                color: #f87171;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                padding: 12px;
                border-radius: 10px;
                text-align: center;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Query Terminal</h1>
                <p>Lightning-fast cloud database lookup</p>
            </div>
            
            <div class="search-box-wrapper">
                <input type="text" id="phone" placeholder="Enter phone number..." autocomplete="off" onkeydown="handleEnter(event)">
            </div>
            <button onclick="searchData()">Execute Query</button>
            
            <div id="status" class="status-msg"></div>
            
            <div id="result-container">
                <div class="result-header">
                    <span>Query Output</span>
                    <button class="copy-btn" onclick="copyResult()">Copy JSON</button>
                </div>
                <pre id="result-box"></pre>
            </div>
        </div>

        <script>
            function handleEnter(event) {
                if (event.key === 'Enter') {
                    searchData();
                }
            }

            async function searchData() {
                const phone = document.getElementById('phone').value.trim();
                const statusDiv = document.getElementById('status');
                const resultContainer = document.getElementById('result-container');
                const resultBox = document.getElementById('result-box');

                if(!phone) {
                    statusDiv.innerHTML = "<div class='error-box'>Please enter a valid phone number.</div>";
                    resultContainer.style.display = 'none';
                    return;
                }

                statusDiv.innerHTML = "Querying distributed parquet store...";
                resultContainer.style.display = 'none';

                try {
                    const response = await fetch('/search/' + encodeURIComponent(phone));
                    const data = await response.json();
                    
                    if(response.ok) {
                        statusDiv.innerHTML = "";
                        resultBox.innerText = JSON.stringify(data, null, 2);
                        resultContainer.style.display = 'block';
                    } else {
                        statusDiv.innerHTML = `<div class='error-box'>${data.detail || "Record not found"}</div>`;
                    }
                } catch(err) {
                    statusDiv.innerHTML = "<div class='error-box'>Network error or gateway timeout.</div>";
                }
            }

            function copyResult() {
                const text = document.getElementById('result-box').innerText;
                navigator.clipboard.writeText(text);
                const btn = document.querySelector('.copy-btn');
                btn.innerText = "Copied!";
                setTimeout(() => btn.innerText = "Copy JSON", 2000);
            }
        </script>
    </body>
    </html>
    """

@app.get("/search/{user_number}")
def search_number(user_number: str):
    try:
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
