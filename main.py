import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from database import create_document, get_documents
from schemas import ContactMessage, BlogPost, Plan

app = FastAPI(title="Shapewear Bodysuit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Shapewear Bodysuit Backend Running"}


# Pricing plans - seed defaults if none exist
DEFAULT_PLANS = [
    Plan(
        name="Essential",
        price=39.0,
        description="Everyday shaping for a smooth silhouette.",
        features=[
            "Breathable fabric",
            "Light-to-medium compression",
            "Seamless under outfits",
        ],
    ),
    Plan(
        name="Sculpt",
        price=69.0,
        description="Targeted compression for confident curves.",
        features=[
            "Tummy & waist shaping",
            "Butt-lift design",
            "Anti-slip straps",
            "All-day comfort",
        ],
        best_value=True,
    ),
    Plan(
        name="Ultra",
        price=99.0,
        description="Maximum control for special occasions.",
        features=[
            "Firm compression",
            "Hourglass support zones",
            "Moisture-wicking",
            "Invisible edges",
        ],
    ),
]


@app.get("/api/pricing", response_model=List[Plan])
def get_pricing():
    try:
        docs = get_documents("plan", {})
        if not docs:
            # seed defaults
            for p in DEFAULT_PLANS:
                create_document("plan", p)
            docs = get_documents("plan", {})
        # transform docs to Plan
        plans: List[Plan] = []
        for d in docs:
            plans.append(
                Plan(
                    name=d.get("name"),
                    price=float(d.get("price", 0)),
                    description=d.get("description"),
                    features=d.get("features", []),
                    best_value=bool(d.get("best_value", False)),
                )
            )
        return plans
    except Exception as e:
        # Fallback to defaults if DB not available
        return DEFAULT_PLANS


# Blog endpoints
class BlogCreate(BaseModel):
    title: str
    excerpt: str | None = None
    content: str
    author: str
    cover_image: str | None = None
    tags: List[str] = []


@app.get("/api/blogs", response_model=List[BlogPost])
def list_blogs():
    try:
        docs = get_documents("blogpost", {}, limit=20)
        return [
            BlogPost(
                title=d.get("title"),
                excerpt=d.get("excerpt"),
                content=d.get("content"),
                author=d.get("author"),
                cover_image=d.get("cover_image"),
                tags=d.get("tags", []),
            )
            for d in docs
        ]
    except Exception:
        # sample posts
        return [
            BlogPost(
                title="How to choose the right shapewear bodysuit",
                excerpt="A quick guide to fit, compression, and comfort.",
                content="Choosing your perfect fit comes down to ...",
                author="Team Lumina",
                cover_image=None,
                tags=["fit", "guide"],
            ),
            BlogPost(
                title="Confidence starts underneath",
                excerpt="Why great foundations change everything.",
                content="Confidence is built from the base up ...",
                author="Editor",
                cover_image=None,
                tags=["confidence"],
            ),
        ]


@app.post("/api/contact")
def submit_contact(message: ContactMessage):
    try:
        create_document("contactmessage", message)
    except Exception:
        pass
    return {"status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
