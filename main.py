from fastapi import FastAPI, HTTPException, Depends
import redis
from models import Contact, User
from schemas import IdentifyRequest, SignUpRequest, LoginRequest
from middlewares import jwt_auth_required, create_jwt_token
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from utils import hash_password, verify_password
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise
from settings import settings
from fastapi import Depends
from tortoise.transactions import in_transaction
from tortoise.expressions import Q
from redis.asyncio import Redis
import json
app = FastAPI()


@app.on_event("startup")
async def init_db():
    await Tortoise.init(
        db_url= settings.PGSQL_DATABASE_URL.replace("postgresql://", "postgres://"),  # Change this
        modules={"models": ["models"]}  # Adjust the path
    )
    await Tortoise.generate_schemas()

# Close connections when shutting down
@app.on_event("shutdown")
async def close_db():
    await Tortoise.close_connections()

# Register Tortoise with FastAPI (optional)
register_tortoise(
    app,
    db_url= settings.PGSQL_DATABASE_URL.replace("postgresql://", "postgres://"),
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


redis = Redis(host=settings.REDIS_HOST, port=6379, db=0, decode_responses=True, ssl=True, password=settings.REDIS_PASSWORD)

async def get_cache_version():
    """Fetch latest cache version to avoid stale data"""
    version = await redis.get("contact_version")
    return int(version) if version else 0

async def bump_cache_version():
    """Increment cache version to invalidate old caches"""
    await redis.incr("contact_version")

@app.post("/identify", dependencies=[Depends(jwt_auth_required)])
async def identify_contact(request: IdentifyRequest):
    cache_key = f"contact:{request.email}-{request.number}"
    
    # Fetch latest version
    latest_version = await get_cache_version()

    # Check if cache exists
    cached_data = await redis.get(cache_key)
    cached_version = await redis.get(f"{cache_key}:version")

    if cached_data and cached_version and int(cached_version) == latest_version:
        return json.loads(cached_data)  # ✅ Return valid cached data

    # ---- Fetch from DB ----
    existing_contacts = await Contact.filter(
        Q(email=request.email) | Q(phone_number=request.number)
    ).all()

    if not existing_contacts:
        async with in_transaction():
            new_contact = await Contact.create(
                phone_number=request.number,
                email=request.email,
                link_precedence="primary"
            )

        response = {
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [new_contact.email],
                "phoneNumbers": [new_contact.phone_number],
                "secondaryContactIds": []
            }
        }

        # Cache the response for a short time
        await redis.set(cache_key, json.dumps(response), ex=10)
        await redis.set(f"{cache_key}:version", latest_version, ex=10)
        return response

    primary_ids = set(contact.link_id if contact.link_id else contact.id for contact in existing_contacts)

    if len(primary_ids) == 1:
        primary_contact = await Contact.get(id=primary_ids.pop())
        secondary_contacts = await Contact.filter(link_id=primary_contact.id)
    else:
        primary_contact = await Contact.get(id=min(primary_ids))
        other_primaries = await Contact.filter(id__in=primary_ids - {primary_contact.id})  

        async with in_transaction():
            for contact in other_primaries:
                contact.link_id = primary_contact.id
                contact.link_precedence = "secondary"
                await contact.save()

            secondaries_to_update = await Contact.filter(link_id__in=primary_ids - {primary_contact.id})
            for contact in secondaries_to_update:
                contact.link_id = primary_contact.id
                await contact.save()

        secondary_contacts = await Contact.filter(link_id=primary_contact.id)

    if request.email and request.number:
        if not any(c.email == request.email and c.phone_number == request.number for c in existing_contacts):
            async with in_transaction():
                new_secondary = await Contact.create(
                    phone_number=request.number,
                    email=request.email,
                    link_precedence="secondary",
                    link_id=primary_contact.id
                )
                secondary_contacts.append(new_secondary)

    response = {
        "contact": {
            "primaryContactId": primary_contact.id,
            "emails": list(set([c.email for c in [primary_contact] + secondary_contacts if c.email])),
            "phoneNumbers": list(set([c.phone_number for c in [primary_contact] + secondary_contacts if c.phone_number])),
            "secondaryContactIds": list(set([c.id for c in secondary_contacts]))
        }
    }

    # Cache response with version tracking
    await redis.set(cache_key, json.dumps(response), ex=10)
    await redis.set(f"{cache_key}:version", latest_version, ex=10)

    return response

# 🚀 Function to clear cache after DB updates
async def clear_cache():
    await bump_cache_version()


@app.post("/signup")
async def user_signup(request: SignUpRequest): 
    existing_user = await User.get_or_none(email=request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    password_hash = hash_password(request.password)
    new_user = await User.create(name=request.name, email=request.email, password=password_hash)
    return {"user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}} 

@app.post("/login")
async def user_login(request: LoginRequest):
    user = await User.get_or_none(email=request.email)
    print(user)
    matching = verify_password(request.password, user.password)
    if not user or not matching:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_jwt_token({"sub": user.email})
    return {"user": {"id": user.id, "name": user.name, "email": user.email, "token": token}}

