import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from schemas import Inquiry
from database import create_document

app = FastAPI(title="Maritime Broker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Maritime Broker API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Public profile information for the broker
class BrokerProfile(BaseModel):
    name: str
    tagline: str
    description: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None

BROKER_PROFILE = BrokerProfile(
    name="Oceanway Maritime Brokerage",
    tagline="Chartering • S&P • Logistics • Consulting",
    description=(
        "We help cargo owners, ship owners and traders move goods across the globe. "
        "From dry bulk and project cargo to tankers and offshore support, our team provides reliable chartering, "
        "sale & purchase advisory, post-fixture support and tailored consulting."
    ),
    email="contact@oceanway-broker.com",
    phone="+44 20 7123 4567",
    location="London • Dubai • Singapore"
)

SERVICES = [
    {
        "title": "Chartering",
        "details": "Dry bulk, tankers, container and project cargo across major global routes."
    },
    {
        "title": "Sale & Purchase",
        "details": "Advisory for vessel acquisitions, disposals and valuations."
    },
    {
        "title": "Logistics",
        "details": "End-to-end logistics planning, port agency coordination and post-fixture."
    },
    {
        "title": "Consulting",
        "details": "Market insights, freight tenders, risk management and strategy."
    }
]

@app.get("/api/profile")
def get_profile():
    return BROKER_PROFILE

@app.get("/api/services")
def get_services():
    return {"services": SERVICES}

@app.post("/api/inquiries")
def create_inquiry(inquiry: Inquiry):
    try:
        inserted_id = create_document("inquiry", inquiry)
        return {"success": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
