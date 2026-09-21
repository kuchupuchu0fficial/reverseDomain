from fastapi import FastAPI, HTTPException
import duckdb

app = FastAPI()

# Yahan apna Hugging Face dataset path daalein
DATA_URL = 'hf://datasets/your_username/your_dataset_name/*.parquet'

@app.get("/search/{user_number}")
def search_number(user_number: str):
    try:
        # DuckDB remote parquet file par direct query chalayega bina download kiye
        query = f"SELECT * FROM read_parquet('{DATA_URL}') WHERE phone_number = '{user_number}'"
        result = duckdb.query(query).to_df()
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Number nahi mila")
        
        return result.to_dict(orient="records")[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
