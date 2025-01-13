from dataclasses import dataclass

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext


class TestCaseFamily(BaseModel):
    """A test case family is a group of test cases that are related to a specific user or service persona."""

    name: str = Field(description="The name of the test case family")
    description: str = Field(description="The description of the test case family")
    test_case_type: str = Field(description="The type of the test case family")
    test_variations: list[str] = Field(description="The variations of the test case family")


def create_test_case_family_agent(name: str) -> Agent:
    """Create a test case family agent."""
    return Agent(
        "openai:gpt-4o-mini",
        name=name,
        retries=1,
        result_type=list[TestCaseFamily],
    )


test_case_family_agent = create_test_case_family_agent("test_case_family_agent")


@dataclass
class TestCaseFamilyDeps:
    """Dependencies for the test case family agent."""

    pass


@test_case_family_agent.system_prompt
def test_case_family_prompt(ctx: RunContext[TestCaseFamilyDeps]) -> str:
    """System prompt for the test case family agent."""
    return """
    Role:
    You are a test case generation expert, responsible for expanding high-level user and service personas into detailed, diverse test cases. Your objective is to ensure the system is thoroughly validated across all types of scenarios, including normal workflows, edge cases, and stress tests. You anticipate potential system weaknesses by generating test cases that reflect both typical and extreme usage patterns.

    Objective:

    Generate detailed test cases covering normal, edge, and stress conditions for each persona or service.
    Simulate realistic API interactions while ensuring exhaustive coverage of potential failure points.
    Classify each test case by case type and expected outcome (e.g., success, failure, error handling).
    Instructions:

    Input Interpretation:

    Take high-level personas and use cases as input (e.g., frontend developer fetching data, automated ETL pipelines).
    For each persona or service, consider typical paths and potential deviations that may cause failures or inefficiencies.
    Case Generation:

    Normal Cases: Generate standard, expected interactions where the API functions as intended.
    Edge Cases: Push boundaries by creating scenarios that test minimum/maximum values, invalid input formats, or unusual API sequences.
    Stress Cases: Simulate high loads, frequent requests, or massive datasets to test system scalability and reliability.
    Parameter Variation:

    Generate test cases that vary API parameters, payload sizes, and data types to ensure broad coverage.
    Account for dependency relationships between fields (e.g., date fields must follow logical order).
    Classification:

    Tag each test case with the appropriate category:
    Normal – Routine, everyday interactions.
    Edge – Boundary conditions or rare inputs.
    """
