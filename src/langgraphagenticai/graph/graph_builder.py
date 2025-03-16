from langgraph.graph import StateGraph, START,END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.state.blog_state import BlogState
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.nodes.chatbot_with_Tool_node import ChatbotWithToolNode
from src.langgraphagenticai.nodes.blog_from_YT_node import BlogFromYTNode
from src.langgraphagenticai.tools.serach_tool import get_tools,create_tool_node
import logging





class GraphBuilder:

    def __init__(self,model,usecase):
        self.llm=model
        if usecase == "Blog from YT VIdeo":
            self.graph_builder=StateGraph(BlogState)
        else:
            self.graph_builder=StateGraph(State)
        self.yt_link = ""

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.basic_chatbot_node=BasicChatbotNode(self.llm)
        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)


    def chatbot_with_tools_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node 
        and a tool node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """
        ## Define the tool and tool node

        tools=get_tools()
        tool_node=create_tool_node(tools)

        ##Define LLM
        llm = self.llm

        # Define chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)

        # Add nodes
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)

        # Define conditional and direct edges
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools","chatbot")

    
    def blog_from_YT_build_graph(self):
        """
        Builds a blog from YouTube graph using LangGraph.
        """

        blog_from_yt_node = BlogFromYTNode(self.llm, self.yt_link)

        self.graph_builder.add_node("transcript_generator", blog_from_yt_node.transcript_generator)
        self.graph_builder.add_node("title_creator", blog_from_yt_node.title_creator)
        self.graph_builder.add_node("content_creator", blog_from_yt_node.content_creator)
        self.graph_builder.add_edge(START, "transcript_generator")
        self.graph_builder.add_edge("transcript_generator", "title_creator")
        self.graph_builder.add_edge("title_creator", "content_creator")
        self.graph_builder.add_edge("content_creator", END)
    
    
    def setup_graph(self, usecase: str, link):
        """
        Sets up the graph for the selected use case.
        """



        if usecase == "Basic Chatbot":
            logging.debug("Basic Chatbot branch executed")
            self.basic_chatbot_build_graph()

        if usecase == "Chatbot with Tool":
            self.chatbot_with_tools_build_graph()
        
        if usecase == "Blog from YT VIdeo":
            self.yt_link = link
            self.blog_from_YT_build_graph()
      
        return self.graph_builder.compile()
    




    

