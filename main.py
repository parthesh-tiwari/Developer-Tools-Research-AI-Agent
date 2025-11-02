from dotenv import load_dotenv
from src.workflows import Workflows

load_dotenv()

def main():
    print("Hello from pythonproject!")

    workflow = Workflows()

    while True:
        query = input("🔬 Enter the developer query !!").strip()
        if query.lower() in ["exit", "quit"]:
            break

        if query:
            result = workflow.run(query)
            print(f"Generated results for : {query}")
            print("=" * 60)

            for i, company in enumerate(result.companies):
                print(f"\n{i}. 🏢 {company.name}")
                print(f"       🌎 Website : {company.website}")
                print(f"       💵 Pricing Model: {company.pricing_model}")
                print(f"       📖 Open Source: {company.is_open_source}")

                if company.tech_stack:
                    print(f"  ⚙️ Tech Stack {', '.join(company.tech_stack[:len(company.tech_stack)])}")

                if company.integration_capabilities:
                    print(
                        f"  🛠️ Integration Capabilities {', '.join(company.integration_capabilities[:len(company.integration_capabilities)])}")

                if company.language_support:
                    print(
                        f"  🛠️ Integration Capabilities {', '.join(company.language_support[:len(company.language_support)])}")

                if company.api_available is not None:
                    api_status = "✅ API Available" if company.api_available else "❌ API Not Available"
                    print(api_status)

                if company.description and company.description != "Analysis Failed":
                    print(f"   📝{company.description}")


                print()

if __name__ == "__main__":
    main()
