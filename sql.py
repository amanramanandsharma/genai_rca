from phi.agent import Agent
from phi.tools.sql import SQLTools

db_url = "mysql+pymysql://root:ServBay.dev@127.0.0.1:3306/breach_db"

agent = Agent(tools=[SQLTools(db_url=db_url)])


if __name__ == "__main__":
    agent.print_response("List the tables in the database. Tell me about contents of one of the breach_data table", markdown=True)