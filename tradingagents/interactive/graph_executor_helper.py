"""
Graph Executor Helper

Provides utilities to execute individual analyst nodes from the LangGraph workflow
for interactive analysis.
"""

from typing import Dict, Any, Optional
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents import (
    create_market_analyst,
    create_social_media_analyst,
    create_news_analyst,
    create_fundamentals_analyst,
)
from tradingagents.agents.analysts.comprehensive_quantitative_analyst import create_comprehensive_quantitative_analyst
from tradingagents.agents.analysts.portfolio_analyst import create_portfolio_analyst
from tradingagents.agents.analysts.enterprise_strategy_analyst import create_enterprise_strategy_analyst
from tradingagents.agents.analysts.visualizer_analyst import create_visualizer_analyst


class GraphExecutorHelper:
    """
    Helper class to execute individual analyst nodes for interactive workflow.

    This class provides methods to run specific analyst nodes in isolation,
    which is needed for the human-in-the-loop interactive workflow.
    """

    # Mapping of analyst types to their state report fields
    ANALYST_REPORT_FIELDS = {
        "market": "market_report",
        "social": "sentiment_report",
        "news": "news_report",
        "fundamentals": "fundamentals_report",
        "quantitative": "quantitative_report",
        "comprehensive_quantitative": "comprehensive_quantitative_report",
        "portfolio": "portfolio_report",
        "enterprise_strategy": "enterprise_strategy_report",
        "visualizer": "visualizer_report",
    }

    def __init__(self, graph: TradingAgentsGraph):
        """
        Initialize helper

        Args:
            graph: TradingAgentsGraph instance
        """
        self.graph = graph

    def execute_analyst_node(
        self,
        analyst_type: str,
        state: AgentState,
        user_context: str = ""
    ) -> tuple[str, AgentState]:
        """
        Execute a single analyst node

        Args:
            analyst_type: Type of analyst ('market', 'fundamentals', etc.)
            state: Current agent state
            user_context: Additional context from user preferences/feedback

        Returns:
            Tuple of (report_string, updated_state)
        """
        # Get the analyst node name
        node_name = f"{analyst_type}_analyst"

        try:
            # Get the node function from the graph
            # LangGraph stores nodes in the graph's internal structure
            # We'll invoke the node directly

            # For LangGraph, we need to get the compiled graph and invoke specific node
            # Since LangGraph doesn't directly support single-node execution,
            # we'll create a minimal subgraph for just this analyst

            # Alternative approach: Call the analyst creation function directly
            analyst_func = self._get_analyst_function(analyst_type)

            if not analyst_func:
                return (f"Error: Analyst type '{analyst_type}' not found", state)

            # Add user context to state messages if provided
            if user_context:
                from langchain_core.messages import HumanMessage
                if "messages" not in state or state["messages"] is None:
                    state["messages"] = []
                state["messages"].append(
                    HumanMessage(content=f"USER CONTEXT:\n{user_context}")
                )

            # Execute the analyst function with tool call loop
            print(f"[DEBUG] Executing {analyst_type} analyst...", flush=True)

            # Import tool executor
            from langchain_core.messages import ToolMessage

            # Execute in a loop to handle tool calls
            max_iterations = 20  # INCREASED: Market analyst needs ~14 iterations (1 for data + 12 indicators + 1 for report)
            iteration = 0

            current_state = state
            while iteration < max_iterations:
                print(f"[DEBUG] === Iteration {iteration} starting ===", flush=True)
                updated_state = analyst_func(current_state)

                # Check if there are tool calls in the last message
                if "messages" in updated_state and updated_state["messages"]:
                    last_message = updated_state["messages"][-1]
                    print(f"[DEBUG] Last message type: {type(last_message).__name__}", flush=True)

                    # Log message content for debugging
                    if hasattr(last_message, 'content'):
                        content_preview = str(last_message.content)[:300] if last_message.content else "None"
                        print(f"[DEBUG] Message content preview: {content_preview}...", flush=True)

                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        # Execute tool calls
                        print(f"[DEBUG] Iteration {iteration}: Found {len(last_message.tool_calls)} tool calls, executing...", flush=True)

                        # Execute tools using the graph's toolkit
                        tool_results = []
                        for tool_call in last_message.tool_calls:
                            tool_name = tool_call["name"]
                            tool_args = tool_call["args"]
                            tool_id = tool_call["id"]

                            print(f"[DEBUG]   - Calling tool: {tool_name}", flush=True)

                            # Get the tool from toolkit
                            toolkit = self.graph.toolkit
                            tool_func = getattr(toolkit, tool_name, None)

                            if tool_func:
                                try:
                                    # Use .invoke() method for LangChain tools
                                    result = tool_func.invoke(tool_args)
                                    result_str = str(result)
                                    print(f"[DEBUG]   - Tool result length: {len(result_str)}", flush=True)
                                    print(f"[DEBUG]   - Tool result preview: {result_str[:200]}...", flush=True)
                                    tool_results.append(
                                        ToolMessage(
                                            content=result_str,
                                            tool_call_id=tool_id,
                                            name=tool_name
                                        )
                                    )
                                except Exception as e:
                                    print(f"[DEBUG]   - Tool error: {str(e)}", flush=True)
                                    tool_results.append(
                                        ToolMessage(
                                            content=f"Error: {str(e)}",
                                            tool_call_id=tool_id,
                                            name=tool_name
                                        )
                                    )
                            else:
                                print(f"[DEBUG]   - Tool not found: {tool_name}", flush=True)
                                tool_results.append(
                                    ToolMessage(
                                        content=f"Tool {tool_name} not found",
                                        tool_call_id=tool_id,
                                        name=tool_name
                                    )
                                )

                        # Add tool results to messages and continue
                        # IMPORTANT: We need to accumulate messages, not replace them
                        # Add the AI message from updated_state
                        current_state["messages"].append(last_message)
                        # Add all tool results
                        current_state["messages"].extend(tool_results)
                        print(f"[DEBUG] Added AI message + {len(tool_results)} tool results. Total messages: {len(current_state['messages'])}", flush=True)

                        # CRITICAL: Clean old messages to prevent context overflow
                        # WatsonX Llama 3.3 70B has 131K token limit
                        # Strategy: Truncate large tool results (like 79K char stock history) while keeping indicator data
                        # BUT: DO NOT truncate news data - every news article is important for analysis

                        # Find and truncate extremely large tool messages (>30K chars)
                        # Only truncate messages that haven't been truncated yet
                        for msg in current_state["messages"]:
                            if hasattr(msg, 'content') and isinstance(msg.content, str):
                                # Check if this is news data (contains "News Coverage Statistics" or "Google News Search Results")
                                is_news_data = "News Coverage Statistics" in msg.content or "Google News Search Results" in msg.content

                                # Only truncate non-news data that is extremely large (>30K chars)
                                # News data (typically 15-20K) should NOT be truncated
                                if not is_news_data and len(msg.content) > 30000 and "[... truncated to save context ...]" not in msg.content:
                                    # This is likely the big stock history data (79K chars)
                                    # Keep first 500 chars (header) + last 500 chars (recent data)
                                    original_len = len(msg.content)
                                    msg.content = msg.content[:500] + f"\n\n[... {original_len - 1000} characters truncated to save context ...]\n\n" + msg.content[-500:]
                                    print(f"[DEBUG] Truncated large tool result: {original_len} chars -> {len(msg.content)} chars", flush=True)

                        # Additionally, if still too many messages, keep recent ones
                        MAX_MESSAGES = 30  # Keep enough for all tool results (13 iterations * 2 + buffer)
                        if len(current_state["messages"]) > MAX_MESSAGES:
                            first_msg = current_state["messages"][0]
                            recent_msgs = current_state["messages"][-(MAX_MESSAGES-1):]
                            current_state["messages"] = [first_msg] + recent_msgs
                            print(f"[DEBUG] Cleaned messages: kept {len(current_state['messages'])} messages", flush=True)

                        iteration += 1
                        continue
                    else:
                        # No tool calls, we're done
                        # CRITICAL: Add the final AI message (the report) to current_state before breaking!
                        print(f"[DEBUG] No tool calls found, analysis complete", flush=True)
                        if hasattr(last_message, 'content'):
                            final_content_preview = str(last_message.content)[:500]
                            print(f"[DEBUG] Final message content (first 500 chars): {final_content_preview}...", flush=True)

                        # Add the final AI message to current_state
                        current_state["messages"].append(last_message)
                        print(f"[DEBUG] Added final AI message. Total messages: {len(current_state['messages'])}", flush=True)
                        break
                else:
                    print(f"[DEBUG] No messages in state, breaking", flush=True)
                    # CRITICAL: Merge updated_state fields into current_state before breaking
                    # This is needed for non-LLM analysts like comprehensive_quantitative that
                    # directly return report fields without generating messages
                    for key, value in updated_state.items():
                        if key != "messages":  # Don't overwrite existing messages
                            current_state[key] = value
                    print(f"[DEBUG] Merged {len([k for k in updated_state.keys() if k != 'messages'])} fields from updated_state", flush=True)
                    break

            if iteration >= max_iterations:
                print(f"[DEBUG] Warning: Reached max iterations ({max_iterations})", flush=True)

            print(f"[DEBUG] Analyst execution completed after {iteration} iterations. Extracting report...", flush=True)

            # IMPORTANT: Use current_state (which has all accumulated messages) instead of updated_state (which only has the last message)
            # This ensures we return the complete state with all tool call history
            final_state = current_state

            # SPECIAL HANDLING FOR NEWS ANALYST: Ensure at least 8 detailed news items
            if analyst_type == "news":
                print(f"[DEBUG] News analyst: Checking if minimum 8 detailed news items were generated...", flush=True)

                # Get the last AI message (the report)
                if "messages" in final_state and final_state["messages"]:
                    last_message = final_state["messages"][-1]
                    if hasattr(last_message, 'content'):
                        report_content = last_message.content

                        # Count how many news items were generated by looking for "### NEWS #" patterns
                        import re
                        news_items = re.findall(r'### NEWS #(\d+):', report_content)
                        num_items = len(news_items)
                        print(f"[DEBUG] News analyst generated {num_items} news items", flush=True)

                        # If fewer than 8 items, add continuation prompt
                        max_continuation_attempts = 2
                        continuation_attempt = 0

                        while num_items < 8 and continuation_attempt < max_continuation_attempts:
                            continuation_attempt += 1
                            print(f"[DEBUG] News analyst: Only {num_items} items found, requesting continuation (attempt {continuation_attempt}/{max_continuation_attempts})...", flush=True)

                            # Add continuation prompt
                            from langchain_core.messages import HumanMessage
                            continuation_msg = HumanMessage(
                                content=f"You have only provided {num_items} news items so far. Please CONTINUE your analysis and provide NEWS #{num_items + 1} through NEWS #10 with DETAILED, FACT-RICH content. Remember, you MUST provide at least 8 news items total with SPECIFIC NUMBERS and DATA that other analysts can reference.\n\nContinue from where you left off with the DETAILED format:\n\n### NEWS #{num_items + 1}: [Full Headline] (source: Source Name, Date)\n**Summary**: 3-4 sentences with SPECIFIC DETAILS (numbers, percentages, dollar amounts, dates, quotes)...\n**Market Impact**: 2-3 sentences analyzing stock price effect and which metrics this affects (P/E, revenue, etc.)...\n**URL**: ..."
                            )
                            current_state["messages"].append(continuation_msg)

                            # Re-invoke the analyst to continue
                            print(f"[DEBUG] Re-invoking news analyst for continuation...", flush=True)
                            continued_state = analyst_func(current_state)

                            if "messages" in continued_state and continued_state["messages"]:
                                continued_message = continued_state["messages"][-1]
                                if hasattr(continued_message, 'content'):
                                    # Append the continuation to our current state
                                    current_state["messages"].append(continued_message)

                                    # Recount news items from ALL messages
                                    all_content = "\n".join([
                                        msg.content for msg in current_state["messages"]
                                        if hasattr(msg, 'content') and isinstance(msg.content, str)
                                    ])
                                    news_items = re.findall(r'### NEWS #(\d+):', all_content)
                                    num_items = len(news_items)
                                    print(f"[DEBUG] After continuation: {num_items} news items total", flush=True)

                            # Update final_state
                            final_state = current_state

                        if num_items >= 8:
                            print(f"[DEBUG] ✅ News analyst: Successfully generated {num_items} detailed news items", flush=True)
                        else:
                            print(f"[DEBUG] ⚠️ News analyst: Only generated {num_items} items after {continuation_attempt} continuation attempts (target: 8-10)", flush=True)

            # Extract the report from the final message
            report_field = self.ANALYST_REPORT_FIELDS.get(analyst_type)
            print(f"\n{'='*70}", flush=True)
            print(f"[REPORT EXTRACTION] Analyst type: {analyst_type}", flush=True)
            print(f"[REPORT EXTRACTION] Expected report field: {report_field}", flush=True)
            print(f"[REPORT EXTRACTION] Final state has {len(final_state.get('messages', []))} messages", flush=True)
            print(f"[REPORT EXTRACTION] Final state keys: {list(final_state.keys())}", flush=True)

            if report_field and report_field in final_state:
                report = final_state[report_field]
                print(f"[DEBUG] Found report in field '{report_field}', length: {len(report) if report else 0}")
                return (report, final_state)
            else:
                # Fallback: try to extract from messages
                print(f"[REPORT EXTRACTION] Report field '{report_field}' not found in state. Using messages fallback...", flush=True)
                if "messages" in final_state and final_state["messages"]:
                    # SPECIAL HANDLING FOR NEWS ANALYST: Merge all AI messages
                    # (because continuation creates multiple AI messages)
                    if analyst_type == "news":
                        from langchain_core.messages import AIMessage
                        ai_messages = [
                            msg for msg in final_state["messages"]
                            if isinstance(msg, AIMessage) and hasattr(msg, 'content') and msg.content
                        ]
                        if len(ai_messages) > 1:
                            print(f"[REPORT EXTRACTION] Found {len(ai_messages)} AI messages for news analyst, merging...", flush=True)
                            # Merge all AI message contents
                            merged_content = "\n\n".join([msg.content for msg in ai_messages])
                            print(f"[REPORT EXTRACTION] Merged content length: {len(merged_content)}", flush=True)
                            print(f"[REPORT EXTRACTION] Merged content preview (first 300 chars): {merged_content[:300]}", flush=True)
                            print(f"{'='*70}\n", flush=True)
                            return (merged_content, final_state)

                    # Default: extract from last message
                    last_message = final_state["messages"][-1]
                    content = last_message.content if hasattr(last_message, 'content') else str(last_message)

                    # CRITICAL FIX: Check if the content is actually a tool call description (JSON format)
                    # This happens when LLM returns JSON instead of a proper analysis report
                    if content and ('"name":' in content or '```json' in content) and len(content) < 1000:
                        print(f"[REPORT EXTRACTION] WARNING: Last message appears to be a tool call description, not a report!", flush=True)
                        print(f"[REPORT EXTRACTION] Attempting to force analyst to generate proper report...", flush=True)

                        # Import HumanMessage for proper message formatting
                        from langchain_core.messages import HumanMessage

                        # Invoke the analyst one more time with explicit instructions to generate a report
                        force_report_state = {
                            **final_state,
                            "messages": final_state["messages"] + [
                                HumanMessage(content="Please analyze ALL the tool results you've received and generate a comprehensive, detailed fundamental analysis report in markdown format. Include financial metrics, valuation ratios, growth trends, and investment recommendations. DO NOT return JSON or tool call descriptions.")
                            ]
                        }

                        # Execute analyst one more time
                        analyst_func = self._get_analyst_function(analyst_type)
                        if analyst_func:
                            try:
                                forced_result = analyst_func(force_report_state)
                                if "messages" in forced_result and forced_result["messages"]:
                                    forced_last = forced_result["messages"][-1]
                                    forced_content = forced_last.content if hasattr(forced_last, 'content') else str(forced_last)
                                    if forced_content and len(forced_content) > len(content):
                                        print(f"[REPORT EXTRACTION] ✅ Successfully forced proper report generation ({len(forced_content)} chars)", flush=True)
                                        content = forced_content
                                        # Update final_state with new messages
                                        final_state["messages"] = forced_result["messages"]
                            except Exception as e:
                                print(f"[REPORT EXTRACTION] ⚠️ Failed to force report generation: {str(e)}", flush=True)

                    print(f"[REPORT EXTRACTION] Extracted from last message, length: {len(content)}", flush=True)
                    print(f"[REPORT EXTRACTION] Content preview (first 300 chars): {content[:300]}", flush=True)
                    print(f"[REPORT EXTRACTION] Returning final_state with {len(final_state.get('messages', []))} messages", flush=True)
                    print(f"{'='*70}\n", flush=True)
                    return (content, final_state)

                print(f"[DEBUG] No report found. State keys: {list(final_state.keys())}")
                error_msg = f"Report generated but field '{report_field}' not found in state. Available fields: {list(final_state.keys())}"
                return (error_msg, final_state)

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f"Error executing {analyst_type} analyst: {str(e)}\n\nDetails:\n{error_detail}"
            return (error_msg, state)

    def _get_analyst_function(self, analyst_type: str):
        """
        Get the analyst node function

        Args:
            analyst_type: Type of analyst

        Returns:
            Callable analyst function or None
        """
        # Get LLM and toolkit from graph
        llm = self.graph.quick_thinking_llm
        toolkit = self.graph.toolkit

        # Map analyst types to their creation functions
        # NOTE: Only use "comprehensive_quantitative" - removed duplicate "quantitative" mapping
        analyst_creators = {
            "market": create_market_analyst,
            "social": create_social_media_analyst,
            "news": create_news_analyst,
            "fundamentals": create_fundamentals_analyst,
            "comprehensive_quantitative": create_comprehensive_quantitative_analyst,  # Only comprehensive version
            "portfolio": create_portfolio_analyst,
            "enterprise_strategy": create_enterprise_strategy_analyst,
            "visualizer": create_visualizer_analyst,
        }

        print(f"[DEBUG] _get_analyst_function called for: {analyst_type}", flush=True)
        print(f"[DEBUG] Available analyst types: {list(analyst_creators.keys())}", flush=True)

        creator_func = analyst_creators.get(analyst_type)
        if creator_func:
            print(f"[DEBUG] Found creator function: {creator_func.__name__}", flush=True)
            # Call the creator function with LLM and toolkit
            # This returns a runnable that takes state and returns updated state
            analyst_node = creator_func(llm, toolkit)
            print(f"[DEBUG] Created analyst node successfully", flush=True)
            return analyst_node

        print(f"[DEBUG] ERROR: No creator found for analyst type: {analyst_type}", flush=True)
        return None

    def create_initial_state(
        self,
        company_of_interest: str,
        trade_date: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AgentState:
        """
        Create initial agent state for analysis

        Args:
            company_of_interest: Stock ticker
            trade_date: Analysis date
            user_preferences: User preferences dictionary

        Returns:
            AgentState object
        """
        state = AgentState(
            company_of_interest=company_of_interest,
            trade_date=trade_date,
            messages=[],
            user_preferences=user_preferences or {}
        )

        return state

    def merge_state_with_report(
        self,
        state: AgentState,
        analyst_type: str,
        report: str
    ) -> AgentState:
        """
        Merge analyst report back into state

        Args:
            state: Current state
            analyst_type: Type of analyst
            report: Report to merge

        Returns:
            Updated state
        """
        report_field = self.ANALYST_REPORT_FIELDS.get(analyst_type)
        if report_field:
            state[report_field] = report

        return state


def create_executor_helper(graph: TradingAgentsGraph) -> GraphExecutorHelper:
    """Factory function to create executor helper"""
    return GraphExecutorHelper(graph)
