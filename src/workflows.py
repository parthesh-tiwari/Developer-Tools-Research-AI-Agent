import os
from typing import Any, Dict

from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain.messages import SystemMessage, HumanMessage
from google import generativeai

from models import CompanyAnalysis, CompanyInformation, CompanyResultState
from firecrawl_service import FireCrawlService
from prompts import DeveloperToolsPrompts

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


class Workflows:

    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not gemini_api_key:
            raise ValueError("Can not find Gemini API key")

        generativeai.configure(api_key=gemini_api_key)

        self.llm = generativeai.GenerativeModel(model_name=MODEL_NAME)
        self.firecrawl = FireCrawlService()
        self.prompt = DeveloperToolsPrompts
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(CompanyResultState)
        # Build graph here
        return graph.compile()

    def _extract_tools_step(self):
        pass

    def _analyze_company_step(self):
        pass

    def _research_step(self):
        pass

    def _analyze_step(self):
        pass

    def run(self):
        pass
