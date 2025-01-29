import os

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.sql import SQLTools

from rag import get_rag_knowledge

db_url = "mysql+pymysql://root:ServBay.dev@127.0.0.1:3306/breach_db"

import typer
from rich.prompt import Prompt
from typing import Optional


sql_agent = Agent(
    name="Breach SQL Agent",
    role="Gets all the Breach related numbers,metrics and data from internal Database",
    model=OpenAIChat(id="gpt-4o"),
    tools=[SQLTools(db_url=db_url)],
    instructions=[
        "Use tables to display data and then summarize the data in one sentence. Always show the SQL query generated"
    ],
    show_tool_calls=True,
    markdown=True,
)

knowledge_agent = Agent(
    name="Breach Knowledge Agent",
    role="Gets all the Breach related knowledge from internal Documents",
    model=OpenAIChat(id="gpt-4o"),
    instructions=["Always get information from internal documents only. Always include sources & references"],
    show_tool_calls=True,
    markdown=True,
    search_knowledge=True,
    knowledge_base=get_rag_knowledge(),
    use_tools=True,
    reasoning=True
)

# agent_team = Agent(
#     team=[sql_agent, knowledge_agent],
#     instructions=[
#         "Use tables to display data and then summarize the data in one sentence. Always show the SQL query generated",
#         "Always include sources",
#     ],
#     show_tool_calls=True,
#     markdown=True,
# )


def manager_agent(user: str = "user"):
    run_id: Optional[str] = None

    agent = Agent(
        team=[sql_agent, knowledge_agent],
        instructions=[
            "Use tables to display data and then summarize the data in one sentence. Always show the SQL query generated",
            "Always get information from internal documents only. Always include sources & references",
        ],
        show_tool_calls=True,
        markdown=True,
    )
    if run_id is None:
        run_id = agent.run_id
        print(f"Started Run: {run_id}\n")
    else:
        print(f"Continuing Run: {run_id}\n")

    while True:
        message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
        if message in ("exit", "bye"):
            break
        agent.print_response(message)


if __name__ == "__main__":
    # Set an environment variable
    typer.run(manager_agent)
