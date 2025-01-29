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
        f'''
            Use tables to display data and then summarize the data in one sentence. Always show the SQL query generated. Do not use any new columns - only use the column defined in the below schema of the table
            Table Name - breach_data
            Columns - 
                week (Week number of the year) - This corresponds to the week number of the year e.g - 44, 45, 46
                breach_bucket (string) - this refers to the breach bucket which can be one of the following - SC breach, RFR, CNR & Other Undel, Not Breached. 
                                            1. SC breach can sometimes be called as NCD or NCD Breach
                                            2. RFR, CNR & Other Undel can sometimes be called as CD or CD Breach
                                            3. Not Breached is the breach bucket which is not breached
                units (int) - total units of shipments
                is_shopsy_order (boolean) - this refers to whether the order was a shopsy order which can be either TRUE or FALSE
                cpd (date) - this refers to the date that was promised for the shipment to be delivered
                breach_sub_bucket (string) - This refers to the asset/warehouse/location where the breach happened. This can be one of the following - FC (Fullfillment Center), MH (Mother hub), FM (First Mile), DH (Delivery Hub), LH (line Haul - basically trucks that move from one warehouse to another), 3PL (Third Party Logistics - which are external vendors who deliver the shipments), LM (last mile)
                service_profile (string) - this has two values 1. FBF (Fullfilled by Flipkart) , 2. NON_FBF (Non Fullfilled by Flipkart) , the difference is that FBF comes from Flipkart's warehouse and NON_FBF comes from other warehouses
                logistics_carrier (string) - this has two values 1. FSD (Flipkart Service Delivery - basically Flipkart delivered this order) & 2. 3PL (Third Party Logistics - which are external vendors who delivered the shipments)
        '''
    ],
    additional_context=f'''
        Refer to the below input & sql pairs to understand the input v/s output sql queries that the user expects. You can also understand what NCD, CD and breach means. 
         - NCD Breach or NCD are same terms
         - CD Breach or CD are same terms
         - Shopsy and Non-Shopsy are refers to the column is_shopsy_order which is either TRUE or FALSE

        1. Input: "How is breach trending in the last few weeks?"
        Query: "SELECT week, ROUND(SUM(CASE WHEN breach_bucket='SC breach' THEN units ELSE 0 END)/SUM(units),3)*100 AS ncd_breach, ROUND(SUM(CASE WHEN breach_bucket='RFR, CNR & Other Undel' THEN units ELSE 0 END)/SUM(units),3)*100 AS cd_breach, ROUND(SUM(CASE WHEN breach_bucket != 'Not Breached' THEN units ELSE 0 END)/SUM(units),3)*100 AS unified_breach FROM breach_data GROUP BY week ORDER BY week;"

        2. Input: "How was NCD or NCD Breach trending in last few weeks?"
        Query: "SELECT week, ROUND(SUM(CASE WHEN breach_bucket='SC breach' THEN units ELSE 0 END)/SUM(units),3)*100 AS ncd_breach FROM breach_data GROUP BY week ORDER BY week;"

        3. Input: "How was CD or CD Breach trending in last few weeks?"
        Query: "SELECT week, ROUND(SUM(CASE WHEN breach_bucket='RFR, CNR & Other Undel' THEN units ELSE 0 END)/SUM(units),3)*100 AS ncd_breach FROM breach_data GROUP BY week ORDER BY week;"

        4. Input: "How is breach between shopsy and non-shopsy trending?"
        Query: "SELECT week, ROUND( SUM( CASE WHEN breach_bucket = 'SC breach' AND is_shopsy_order = 'TRUE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'TRUE' then units ELSE 0 END ), 3 ) * 100 AS shopsy_ncd_breach, ROUND( SUM( CASE WHEN breach_bucket = 'SC breach' AND is_shopsy_order = 'FALSE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'FALSE' then units ELSE 0 END ), 3 ) * 100 AS non_shopsy_ncd_breach, ROUND( SUM( CASE WHEN breach_bucket = 'RFR, CNR & Other Undel' AND is_shopsy_order = 'TRUE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'TRUE' then units ELSE 0 END ), 3 ) * 100 AS shopsy_cd_breach, ROUND( SUM( CASE WHEN breach_bucket = 'RFR, CNR & Other Undel' AND is_shopsy_order = 'FALSE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'FALSE' then units ELSE 0 END ), 3 ) * 100 AS non_shopsy_cd_breach, ROUND( SUM( CASE WHEN breach_bucket != 'Not Breached' AND is_shopsy_order = 'TRUE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'TRUE' then units ELSE 0 END ), 3 ) * 100 AS shopsy_unified_breach, ROUND( SUM( CASE WHEN breach_bucket != 'Not Breached' AND is_shopsy_order = 'FALSE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'FALSE' then units ELSE 0 END ), 3 ) * 100 AS non_shopsy_unified_breach FROM breach_data GROUP BY week ORDER BY week"

        5. How is Shopsy Breach trending in the last few weeks?
        Query: "SELECT week, ROUND( SUM( CASE WHEN breach_bucket = 'SC breach' AND is_shopsy_order = 'TRUE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'TRUE' then units ELSE 0 END ), 3 ) * 100 AS shopsy_ncd_breach, ROUND( SUM( CASE WHEN breach_bucket = 'RFR, CNR & Other Undel' AND is_shopsy_order = 'TRUE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'TRUE' then units ELSE 0 END ), 3 ) * 100 AS shopsy_cd_breach, ROUND( SUM( CASE WHEN breach_bucket != 'Not Breached' AND is_shopsy_order = 'TRUE' THEN units ELSE 0 END ) / SUM( CASE WHEN is_shopsy_order = 'TRUE' then units ELSE 0 END ), 3 ) * 100 AS shopsy_unified_breach FROM breach_data GROUP BY week ORDER BY week"

    ''',
    show_tool_calls=True,
    markdown=True
)

knowledge_agent = Agent(
    name="Breach Knowledge Agent",
    role="Gets all the Breach related knowledge from internal Documents",
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Always get information from internal documents only. Always include sources & references. If information is not found say that the information was not available in the internal documents"
    ],
    show_tool_calls=True,
    markdown=True,
    search_knowledge=True,
    knowledge_base=get_rag_knowledge(),
    use_tools=True,
    enable_rag=True,
    prevent_hallucinations=True,
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
            "Always get information from internal documents only. Always include sources & references. If information is not found say that the information was not available in the internal documents",
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
