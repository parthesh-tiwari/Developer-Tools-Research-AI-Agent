import os
from typing import Any, Dict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain.messages import SystemMessage, HumanMessage
from google.genai import Client, types
from google import generativeai

from src.models import CompanyAnalysis, CompanyInformation, CompanyResultState
from src.firecrawl_service import FireCrawlService
from src.prompts import DeveloperToolsPrompts

load_dotenv()
MODEL_NAME = "gemini-2.5-flash"


class Workflows:
    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Can not find Gemini API key")
        self.llm_client = Client(api_key=gemini_api_key)
        generativeai.configure(api_key=gemini_api_key)
        self.llm = generativeai.GenerativeModel(
            model_name=MODEL_NAME
        )
        self.firecrawl = FireCrawlService()
        self.prompt = DeveloperToolsPrompts
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(CompanyResultState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("analyze", self._analyze_step)
        graph.add_node("research", self._research_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: CompanyResultState) -> Dict[str, Any]:
        print("Step for tools extraction")
        search_query = f"{state.query} tools comparison best alternatives"
        results = self.firecrawl.search_companies(query=search_query, top_k=5)
        docs_list = getattr(results, "web", [])  # Use .web to get the list

        all_content = ""
        for doc in docs_list:
            if hasattr(doc, "markdown"):
                all_content += doc.markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompt.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompt.tool_extraction_user(query=state.query, content=all_content))
        ]
        try:
            response = self.llm.generate_content(messages)
            tools = [
                name.strip()
                for name in response.text.strip().split("\n")
                if name.strip()
            ]
            print(f"Extracted tools : {' ,'.join(tools[:5])}")
            return {
                "extracted_tools": tools
            }
        except Exception as e:
            print(e)
            return {
                "extracted_tools": []
            }

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        messages = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(
                    text=self.prompt.TOOL_EXTRACTION_SYSTEM
                         + "\n\n"
                         + self.prompt.tool_analysis_user(company_name=company_name, content=content)
                )]
            )
        ]
        try:
            analysis = self.llm_client.models.generate_content(
                model=MODEL_NAME,
                contents=messages,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CompanyAnalysis
                )
            )
            return CompanyAnalysis.parse_raw(analysis.text)
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                tech_stack=[],
                is_open_source=None,
                description="",
                language_support=[],
                api_available=None,
                integration_capabilities=[]
            )

    def _research_step(self, state: CompanyResultState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])
        if not extracted_tools:
            print("No extracted tools found, falling back to default search")
            search_results = self.firecrawl.search_companies(query=state.query, top_k=4)
            docs_list = getattr(search_results, "web", [])
            tool_names = [
                doc.markdown.splitlines()[0] if hasattr(doc, "markdown") and doc.markdown else "Unknown"
                for doc in docs_list
            ]
        else:
            tool_names = extracted_tools[:4]
        print(f"Researching specific tools : {', '.join(tool_names)}")
        companies = []
        for tool_name in tool_names:
            tools_search_results = self.firecrawl.search_companies(query=tool_name + " company names", top_k=1)
            docs_list = getattr(tools_search_results, "web", [])  # Always use .web
            if docs_list and hasattr(docs_list[0], "markdown"):
                first_doc = docs_list[0]
                company = CompanyInformation(
                    tech_stack=[],
                    competitors=[],
                    website="",
                    description=first_doc.markdown,
                    pricing_model="Unknown",
                    name=tool_name
                )
                content = first_doc.markdown
                analysis = self._analyze_company_content(company_name=company.name, content=content)
                company.api_available = analysis.api_available
                company.tech_stack = analysis.tech_stack
                company.competitors = getattr(analysis, "competitors", [])
                company.is_open_source = analysis.is_open_source
                company.integration_capabilities = analysis.integration_capabilities
                company.description = analysis.description
                company.pricing_model = analysis.pricing_model
                company.language_support = analysis.language_support
                company.developer_experience_rating = getattr(analysis, "developer_experience_rating", None)
                companies.append(company)
        return {"companies": companies}

    def _analyze_step(self, state: CompanyResultState) -> Dict[str, Any]:
        print("Generating recommendations !")
        companies = ', '.join(
            [company.model_dump_json() for company in state.companies]
        )
        messages = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(
                    text=self.prompt.RECOMMENDATIONS_SYSTEM
                         + "\n\n"
                         + self.prompt.recommendations_user(query=state.query, company_data=companies)
                )]
            )
        ]
        analysis = self.llm_client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
        )
        return {
            "analysis": analysis.text
        }

    def run(self, query: str):
        initial_state = CompanyResultState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return CompanyResultState(**final_state)
