import asyncio
from dataclasses import dataclass

from fastapi import FastAPI
from pydantic_settings import BaseSettings

from ai_api_testing.agents.api_specs_agents.fastapi_extractor import (
    APIEndpoint,
    FastAPISpecsExtractor,
)
from ai_api_testing.agents.api_specs_agents.swagger_extractor import SwaggerExtractor
from ai_api_testing.utils.logger import logger
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel


class Settings(BaseSettings):
    """Environment settings."""

    OPENAI_API_KEY: str

    class Config:
        """Environment configuration."""

        env_file = ".env"


@dataclass
class Deps:
    """Dependencies."""

    app: FastAPI


model = OpenAIModel("gpt-4o-mini", api_key=Settings().OPENAI_API_KEY)

agent_specs_extractor = Agent(
    model,
    system_prompt=(
        "You are an agent that extracts and analyzes API specifications"
        "from a FastAPI app or from Swagger/OpenAPI specification. First try to find the json one time, and if not parse the docs available on the root path."
    ),
    deps_type=Deps,
    retries=3,
)


@agent_specs_extractor.tool
async def extract_fastapi_specs(ctx: RunContext[Deps]) -> list[APIEndpoint]:
    """Extract the API specifications from a FastAPI application.

    Args:
        ctx: The context.
    """
    # TODO: Remove this once the tool is implemented
    return """
    APIEndpoint(path='/predict', method='POST', request_body={'properties': {'tweet_text': {'type': 'string', 'title': 'Tweet
    Text', 'description': 'The actual text content of the tweet'}, 'author_followers': {'type': 'integer', 'title': 'Author Followers', 'description': 'Number of followers the tweet author has'}, 'author_following': {'type': 'integer', 'title': 'Author Following', 'description': 'Number of accounts the author follows'}, 'author_verified': {'type': 'boolean', 'title': 'Author Verified', 'description': 'Whether the author is verified', 'default': False}, 'tweet_has_media': {'type': 'boolean',
    'title': 'Tweet Has Media', 'description': 'Whether the tweet contains media (images/videos)', 'default': False}, 'tweet_has_links': {'type': 'boolean', 'title': 'Tweet Has Links', 'description': 'Whether the tweet contains URLs', 'default': False}, 'tweet_has_hashtags': {'type': 'boolean', 'title': 'Tweet Has Hashtags', 'description': 'Whether the tweet contains hashtags', 'default': False}, 'tweet_reply_count': {'type': 'integer', 'title': 'Tweet Reply Count', 'description': 'Number of replies to this tweet', 'default': 0}, 'tweet_retweet_count': {'type': 'integer', 'title': 'Tweet Retweet Count', 'description': 'Number of retweets', 'default': 0}, 'tweet_like_count': {'type': 'integer', 'title': 'Tweet Like Count', 'description': 'Number of likes', 'default': 0}, 'tweet_quote_count': {'type': 'integer', 'title': 'Tweet Quote Count', 'description': 'Number of quote tweets', 'default': 0}}, 'type': 'object', 'required': ['tweet_text', 'author_followers', 'author_following'], 'title': 'TweetScoreInput', 'description': 'Tweet score input model.'}"""
    return FastAPISpecsExtractor().extract_specs(app=ctx.deps.app)


@agent_specs_extractor.tool
async def extract_swagger_specs(
    ctx: RunContext[Deps], url: str, endpoint_list: list[str] | None = None
) -> list[APIEndpoint]:
    """Extract the API specifications from a Swagger/OpenAPI specification.

    Args:
        ctx: The context.
        url: The URL of the Swagger/OpenAPI specification.
        endpoint_list: The list of endpoints to extract. If None, all endpoints are extracted.
    """
    logger.info(f"Extracting Swagger/OpenAPI specification from {url}, endpoint_list: {endpoint_list}")
    return await SwaggerExtractor().extract_endpoints(url, endpoint_list)


async def main(url: str):
    """Main function."""
    app = FastAPI()

    deps = Deps(app=app)
    result = await agent_specs_extractor.run(
        f"""What is the request body for {url} endpoints?
        Try with the json and if not parse the docs available on {url} root path""",
        deps=deps,
    )
    print("Response:", result.data)


if __name__ == "__main__":
    asyncio.run(main("https://petstore.swagger.io"))
