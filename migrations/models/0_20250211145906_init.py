from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "contact" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phone_number" VARCHAR(20) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "link_precedence" VARCHAR(50) NOT NULL,
    "link_id" INT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS "idx_contact_phone_n_aa1407" ON "contact" ("phone_number");
CREATE INDEX IF NOT EXISTS "idx_contact_email_815930" ON "contact" ("email");
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "role" VARCHAR(5) NOT NULL DEFAULT 'user'
);
CREATE INDEX IF NOT EXISTS "idx_user_name_76f409" ON "user" ("name");
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
COMMENT ON COLUMN "user"."role" IS 'USER: user\nADMIN: admin';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
