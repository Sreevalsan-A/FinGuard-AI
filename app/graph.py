from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.llm import llm
from app.finance_tools import (
    calculate_invoice_total,
    calculate_variance,
    check_budget_status,
    detect_duplicate_invoice,
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools = [
    calculate_invoice_total,
    calculate_variance,
    check_budget_status,
    detect_duplicate_invoice,
]

llm_with_tools = llm.bind_tools(tools)


def finance_agent(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


tool_node = ToolNode(tools)


def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


graph_builder = StateGraph(AgentState)

graph_builder.add_node("finance_agent", finance_agent)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "finance_agent")

graph_builder.add_conditional_edges(
    "finance_agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

graph_builder.add_edge("tools", "finance_agent")

finance_graph = graph_builder.compile()