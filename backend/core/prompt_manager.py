"""
prompt_manager.py
-----------------
Her STLC adımı için MongoDB'den system prompt ve query_str gibi verileri çekmeye yarar.
Ayrıca structured_output formatı gibi ilave bilgileri de buradan alabilirsiniz.
"""

import logging
from core.database import get_db
from datetime import datetime

# Logger ayarları
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
def initialize_test_planning_prompt():
    db = get_db()
    # Yeni koleksiyon adı: test_planning_prompt
    if "test_planning_prompt" not in db.list_collection_names():
        db.create_collection("test_planning_prompt")
        print("test_planning_prompt koleksiyonu oluşturuldu.")
    # Prompt'u ekle
    prompt = {
        "process_type": "test_planning",
        "prompt_text": """Analyze the following project materials as an ISTQB expert and use the information provided to generate a comprehensive test planning schedule that adheres strictly to ISTQB standards. Your objective is to produce a detailed test planning document, optimized for creating a Gantt chart. Your analysis should cover all aspects of test planning, including test strategy, resource estimation, scheduling, risk management, and environment/tool requirements. You must focus solely on constructing the test planning schedule, without incorporating the content of the input documents verbatim.

When generating dates in your output, use the current date "{today}" as the starting point for scheduling. All planned dates should be calculated relative to today's date.

Your output must be a valid JSON array where each object represents a task in the test planning process. Each object must contain exactly the following keys:
- "Task Name": A concise title for the task.
- "Description": A detailed explanation of the task, including all necessary ISTQB-standard test planning elements.
- "Start Date": The planned start date for the task in the format YYYY-MM-DD.
- "End Date": The planned end date for the task in the format YYYY-MM-DD.
- "Duration (days)": The total number of days allocated for the task.
{today}+x :example {today}+5="2025-05-02"
If you were to make such an addition it would be wrong 2025-04-27+5
Below is an example JSON structure to follow:

[
    {{
        "Task Name": "Test Strategy Definition",
        "Description": "Define the overall testing strategy, including objectives, scope (in-scope and out-of-scope items), success criteria, and exit conditions, based on ISTQB standards.",
        "Start Date": "{today}",
        "End Date": "{today}+4",
        "Duration (days)": 5
    }},
    {{
        "Task Name": "Resource Estimation and Scheduling",
        "Description": "Estimate the required testing resources and develop a realistic schedule that aligns with project deadlines following ISTQB best practices.",
        "Start Date": "{today}+5",
        "End Date": "{today}+9",
        "Duration (days)": 5
    }},
    {{
        "Task Name": "Risk Assessment and Mitigation Planning",
        "Description": "Identify potential risks related to security, performance, and usability. Develop mitigation strategies and contingency plans in line with ISTQB standards.",
        "Start Date": "{today}+10",
        "End Date": "{today}+14",
        "Duration (days)": 5
    }},
    {{
        "Task Name": "Test Environment and Tool Setup",
        "Description": "Define and set up the test environment, including hardware, software, network configurations, and necessary test tools, ensuring full compliance with ISTQB guidelines.",
        "Start Date": "{today}+15,
        "End Date": "{today}+19",
        "Duration (days)": 5
    }}
]

*Additional Instructions:*
- Ensure that the output JSON array is directly convertible into an XLSX spreadsheet, where each key represents a column header.
- Do not include any extra keys or unstructured text outside of the JSON array.
- Your analysis must reflect the expertise of an ISTQB expert and provide a comprehensive test planning schedule that aligns with ISTQB standards.
- Instead of processing a test planning document, use the content provided (which may be from other types of documents) to generate a test planning schedule.
- The output should be detailed and cover all essential aspects of the test planning process without including any feedback or recommendations.
- Use the current date "{today}" as a reference point for all scheduled dates in the generated output..""",
        "system_suffix": """Test planning for the following:\nToday's date: {today}\nProject code:\n{code}\nRequirements document:\n{requirement_document}""",
        "description": "Base prompt for test planning process",
        "created_at": datetime.now()
    }
    existing = db.test_planning_prompt.find_one({"process_type": "test_planning"})
    if not existing:
        db.test_planning_prompt.insert_one(prompt)
        print("Test planning prompt eklendi.")
    else:
        print("Test planning prompt zaten mevcut.")

def initialize_code_review_prompt():
    db = get_db()
    if "code_review_prompt" not in db.list_collection_names():
        db.create_collection("code_review_prompt")
    prompt = {
        "process_type": "code_review",
        "prompt_text": """Please perform a comprehensive code review of the following codebase. If no Requirement Document is provided, skip the Requirement Compliance section entirely (do not attempt to infer requirements from the code).

Focus on:
1. Requirement Compliance: Check whether the code correctly implements the functionalities and specifications outlined in the Requirement Document. List missing, incomplete, or incorrectly implemented requirements.
2. Overall Architecture and Code Organization: Evaluate the code structure, modularity, and maintainability.
3. Code Quality and Best Practices: Assess naming conventions, readability, documentation, and adherence to best coding practices.
4. Potential Bugs and Issues: Identify any logical errors, edge cases, or potential failures.
5. Security Considerations: Detect vulnerabilities such as lack of input validation, hardcoded credentials, or insecure storage of sensitive data.
6. Performance Implications: Analyze any inefficient code patterns or resource-heavy operations.
7. Suggestions for Improvement: Provide actionable recommendations for improving the codebase and fulfilling any missing requirements.

Please organize your response clearly under each section, and provide specific examples and detailed recommendations where applicable..""",
        "system_suffix": "Code to review:\n{code}",
        "description": "Base prompt for code review process",
        "created_at": datetime.now()
    }
    existing = db.code_review_prompt.find_one({"process_type": "code_review"})
    if not existing:
        db.code_review_prompt.insert_one(prompt)
        print("Code review prompt eklendi.")
    else:
        print("Code review prompt zaten mevcut.")
    if "session_history" not in db.list_collection_names():
        db.create_collection("session_history")
        print("session_history koleksiyonu oluşturuldu.")
def initialize_prompt():
    db = get_db()
    # Yeni koleksiyon adı: code_review_prompt
    if "code_review_prompt" not in db.list_collection_names():
        db.create_collection("code_review_prompt")
        print("code_review_prompt koleksiyonu oluşturuldu.")
    # Prompt'u ekle
    prompt = {
        "process_type": "code_review",
        "prompt_text": """Please perform a comprehensive code review of the following codebase. If no Requirement Document is provided, skip the Requirement Compliance section entirely (do not attempt to infer requirements from the code).

Focus on:
1. Requirement Compliance: Check whether the code correctly implements the functionalities and specifications outlined in the Requirement Document. List missing, incomplete, or incorrectly implemented requirements.
2. Overall Architecture and Code Organization: Evaluate the code structure, modularity, and maintainability.
3. Code Quality and Best Practices: Assess naming conventions, readability, documentation, and adherence to best coding practices.
4. Potential Bugs and Issues: Identify any logical errors, edge cases, or potential failures.
5. Security Considerations: Detect vulnerabilities such as lack of input validation, hardcoded credentials, or insecure storage of sensitive data.
6. Performance Implications: Analyze any inefficient code patterns or resource-heavy operations.
7. Suggestions for Improvement: Provide actionable recommendations for improving the codebase and fulfilling any missing requirements.

Please organize your response clearly under each section, and provide specific examples and detailed recommendations where applicable..""",
        "system_suffix": "Code to review:\n{code}",
        "description": "Base prompt for code review process",
        "created_at": datetime.now()
    }
    existing = db.code_review_prompt.find_one({"process_type": "code_review"})
    if not existing:
        db.code_review_prompt.insert_one(prompt)
        print("Code review prompt eklendi.")
    else:
        print("Code review prompt zaten mevcut.")
    if "session_history" not in db.list_collection_names():
        db.create_collection("session_history")
        print("session_history koleksiyonu oluşturuldu.")
def initialize_requirement_analysis_prompt():
    db = get_db()
    # Yeni koleksiyon adı: requirement_analysis_prompt
    if "requirement_analysis_prompt" not in db.list_collection_names():
        db.create_collection("requirement_analysis_prompt")
        print("requirement_analysis_prompt koleksiyonu oluşturuldu.")
    # Prompt'u ekle
    prompt = {
        "process_type": "requirement_analysis",
        "prompt_text": """Please perform a comprehensive Requirement Analysis for the following codebase, comparing it against the provided Requirement Document. 
Focus on:
1.Requirement Compliance: Check whether the code correctly implements the functionalities and specifications outlined in the Requirement Document. Identify any missing, incomplete, or incorrectly implemented requirements. Provide specific examples from the code to demonstrate where the implementation deviates from the expected requirements.
2.Functional Coverage: Ensure that all the functional requirements from the Requirement Document are covered in the codebase. If any functionality is missing or not fully implemented, note it down with details.
3.Design and Architecture Alignment: Analyze whether the design and architecture of the code align with the high-level system design as outlined in the Requirement Document.
4.Edge Case Handling: Verify whether the code correctly handles edge cases and special scenarios that are mentioned in the Requirement Document.
5.Non-Functional Requirements: Ensure that non-functional requirements, such as performance, security, scalability, and maintainability, are addressed as per the document.
6.Suggestions for Improvement: Provide actionable recommendations for making the code better aligned with the documented requirements.
Please organize your response clearly under each section and provide detailed examples and recommendations where applicable.""",
        "system_suffix": "Codebase:\n{code}\n\nRequirement Document:\n{requirement_document}",
        "description": "Base prompt for requirement analysis process",
        "created_at": datetime.now()
    }
    existing = db.requirement_analysis_prompt.find_one({"process_type": "requirement_analysis"})
    if not existing:
        db.requirement_analysis_prompt.insert_one(prompt)
        print("Requirement analysis prompt eklendi.")
    else:
        print("Requirement analysis prompt zaten mevcut.")

def get_prompts_for_step(step_name: str):
    """
    Belirtilen STLC adımı için MongoDB'den prompt bilgilerini çeker.
    
    :param step_name: STLC adımı (örneğin, "test_planning").
    :return: system_prompt, query_str ve structured_output_schema içeren bir sözlük.
    """
    logger.info(f"{step_name} adımı için prompt bilgileri çekiliyor.")
    
    try:
        db = get_db()
        collection = db["test_scenario_generation_prompts"]  # Koleksiyon adı
        document = collection.find_one({"step": step_name})
        
        if document:
            logger.info(f"{step_name} adımı için prompt bilgileri bulundu.")
            return {
                "system_prompt": document.get("system_prompt", ""),
                "query_str": document.get("query_str", ""),
                "structured_output_schema": document.get("structured_output_schema", {})
            }
        else:
            logger.warning(f"{step_name} adımı için prompt bilgileri bulunamadı.")
            return {}
    except Exception as e:
        logger.error(f"Prompt bilgileri çekilirken hata oluştu: {str(e)}")
        return {}
def initialize_environment_setup_prompt():
    db = get_db()
    if "environment_setup_prompt" not in db.list_collection_names():
        db.create_collection("environment_setup_prompt")
        print("environment_setup_prompt koleksiyonu oluşturuldu.")
    prompt = {
        "process_type": "environment_setup",
        "prompt_text": """You are responsible for preparing the environment setup as part of the Software Testing Life Cycle (STLC) process.
You will be given:

Source code files (such as requirements.txt, package.json, pom.xml, etc.)

Additional requirement information (like preferred OS, database type, language version)

Based on the provided input, your task is:

Identify the programming language and its required version.

Identify the main frameworks or libraries used.

Recommend a suitable operating system (such as Windows 10+, Ubuntu 20.04+, macOS).

List all dependencies.

Specify the required database (if any).

List additional required tools (e.g., pip, venv, npm, Maven).

Write important installation notes (e.g., \"Python 3.10+ must be installed\", \"PostgreSQL client tools required\", etc.)

}""",
        "system_suffix": (
    "Output Format:\n"
    "Don't make any explanation, just give the json structure. Otherwise, the program may crash, just give the json structure.\n"
    "You must output your result in JSON format with the following structure. The following is just an example. Fill in the variables according to the scheme, whatever should come in the files you throw in.:\n\n"
    "{{\n"
    "  \"environment_setup\": {{\n"
    "    \"language\": \"Python\",\n"
    "    \"language_version\": \">=3.9\",\n"
    "    \"framework\": \"Flask\",\n"
    "    \"operating_system\": \"Ubuntu 20.04\",\n"
    "    \"dependencies\": [\n"
    "      \"Flask==2.2.2\",\n"
    "      \"requests>=2.26\",\n"
    "      \"gunicorn>=20.1.0\"\n"
    "    ],\n"
    "    \"database\": \"Not Required\",\n"
    "    \"required_tools\": [\n"
    "      \"pip\",\n"
    "      \"virtualenv\"\n"
    "    ],\n"
    "    \"installation_notes\": \"...\"\n"
    "  }}\n"
    "}}\n\n"
    "Source Code:\n{code}\n"
    "Requirement Document:\n{requirement_document}"
),
        "description": "Base prompt for environment setup process",
        "created_at": datetime.now()
    }
    existing = db.environment_setup_prompt.find_one({"process_type": "environment_setup"})
    if not existing:
        db.environment_setup_prompt.insert_one(prompt)
        print("Environment setup prompt eklendi.")
    else:
        print("Environment setup prompt zaten mevcut.")

# Bu fonksiyonu çalıştır
initialize_prompt()
initialize_requirement_analysis_prompt()
initialize_test_planning_prompt()
initialize_environment_setup_prompt()
def get_base_prompt(process_type: str):
    """
    Belirtilen süreç için ilgili _prompt koleksiyonundan temel prompt'u çeker.
    """
    logger.info(f"{process_type} süreci için temel prompt çekiliyor.")
    try:
        db = get_db()
        collection_name = f"{process_type}_prompt"
        collection = db[collection_name]
        document = collection.find_one({"process_type": process_type})
        if document:
            logger.info(f"{process_type} süreci için temel prompt bulundu.")
            return document.get("prompt_text", "")
        else:
            logger.warning(f"{process_type} süreci için temel prompt bulunamadı.")
            return None
    except Exception as e:
        logger.error(f"Temel prompt çekilirken hata oluştu: {str(e)}")
        return None

def save_session_data(session_data: dict, process_type: str = "code_review"):
    """
    Her session_id için tek bir doküman, ilgili süreç (örn. code_review, requirement_analysis) için şu alanları kaydeder/günceller:
    - output: çıktı
    - edited_prompt: base prompt değişti mi (True/False)
    - used_prompt: kullanılan prompt metni
    - used_model: kullanılan AI model
    """
    logger.info(f"Session verisi kaydediliyor/güncelleniyor ({process_type} için özel alanlar).")
    try:
        db = get_db()
        collection = db["session_history"]
        session_id = session_data.get("session_id")
        output = session_data.get("output")
        edited_prompt = session_data.get("edited_prompt")
        used_prompt = session_data.get("used_prompt")
        used_model = session_data.get("used_model")

        if not session_id or output is None or edited_prompt is None or used_prompt is None:
            logger.warning("Eksik session verisi: session_id, output, edited_prompt veya used_prompt yok.")
            return None

        # Güncellenecek alan: processes.{process_type}
        update_field = {
            f"processes.{process_type}": {
                "output": output,
                "edited_prompt": edited_prompt,
                "used_prompt": used_prompt,
                "used_model": used_model,
                "timestamp": datetime.now()
            }
        }

        # Upsert işlemi: varsa güncelle, yoksa oluştur
        result = collection.update_one(
            {"session_id": session_id},
            {
                "$set": update_field,
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
        logger.info(f"Session güncellendi/upsert edildi. session_id: {session_id}, process: {process_type}")
        return result.upserted_id or result.modified_count
    except Exception as e:
        logger.error(f"Session verisi kaydedilirken hata oluştu: {str(e)}")
        return None

def initialize_base_prompts():
    """
    Veritabanına temel promptları ekler (sadece ilk kez çalıştırılmalı).
    Hem code_review hem requirement_analysis için çalışır.
    """
    logger.info("Temel promptlar başlatılıyor.")
    try:
        db = get_db()
        # --- CODE REVIEW PROMPT ---
        collection = db["code_review_prompt"]
        if collection.count_documents({}) == 0:
            code_review_prompt = """Please perform a comprehensive code review of the following codebase. If no Requirement Document is provided, skip the Requirement Compliance section entirely (do not attempt to infer requirements from the code).

Focus on:
1. Requirement Compliance: Check whether the code correctly implements the functionalities and specifications outlined in the Requirement Document. List missing, incomplete, or incorrectly implemented requirements.
2. Overall Architecture and Code Organization: Evaluate the code structure, modularity, and maintainability.
3. Code Quality and Best Practices: Assess naming conventions, readability, documentation, and adherence to best coding practices.
4. Potential Bugs and Issues: Identify any logical errors, edge cases, or potential failures.
5. Security Considerations: Detect vulnerabilities such as lack of input validation, hardcoded credentials, or insecure storage of sensitive data.
6. Performance Implications: Analyze any inefficient code patterns or resource-heavy operations.
7. Suggestions for Improvement: Provide actionable recommendations for improving the codebase and fulfilling any missing requirements.

Please organize your response clearly under each section, and provide specific examples and detailed recommendations where applicable.


Code to review:
{code}"""
            collection.insert_one({
                "process_type": "code_review",
                "prompt_text": code_review_prompt,
                "description": "Base prompt for code review process",
                "created_at": datetime.now()
            })
            logger.info("Code review base prompt başarıyla yüklendi.")
        else:
            logger.info("Code review base prompt zaten mevcut, yükleme atlanıyor.")
        # --- REQUIREMENT ANALYSIS PROMPT ---
        req_collection = db["requirement_analysis_prompt"]
        if req_collection.count_documents({}) == 0:
            requirement_analysis_prompt = """Please perform a comprehensive Requirement Analysis for the following codebase, comparing it against the provided Requirement Document. Focus on:
1.Requirement Compliance: Check whether the code correctly implements the functionalities and specifications outlined in the Requirement Document. Identify any missing, incomplete, or incorrectly implemented requirements. Provide specific examples from the code to demonstrate where the implementation deviates from the expected requirements.
2.Functional Coverage: Ensure that all the functional requirements from the Requirement Document are covered in the codebase. If any functionality is missing or not fully implemented, note it down with details.
3.Design and Architecture Alignment: Analyze whether the design and architecture of the code align with the high-level system design as outlined in the Requirement Document.
4.Edge Case Handling: Verify whether the code correctly handles edge cases and special scenarios that are mentioned in the Requirement Document.
5.Non-Functional Requirements: Ensure that non-functional requirements, such as performance, security, scalability, and maintainability, are addressed as per the document.
6.Suggestions for Improvement: Provide actionable recommendations for making the code better aligned with the documented requirements.
Please organize your response clearly under each section and provide detailed examples and recommendations where applicable."""
            req_collection.insert_one({
                "process_type": "requirement_analysis",
                "prompt_text": requirement_analysis_prompt,
                "description": "Base prompt for requirement analysis process",
                "created_at": datetime.now()
            })
            logger.info("Requirement analysis base prompt başarıyla yüklendi.")
        else:
            logger.info("Requirement analysis base prompt zaten mevcut, yükleme atlanıyor.")
        return True
    except Exception as e:
        logger.error(f"Temel promptlar yüklenirken hata oluştu: {str(e)}")
        return False

def save_custom_prompt(process_type: str, prompt_text: str):
    """
    Sadece yeni bir base prompt ekler. Eğer process_type için zaten bir base prompt varsa, hiçbir değişiklik yapmaz.
    Kullanıcılar base promptu değiştiremez.
    :param process_type: Prompt'un ilişkili olduğu süreç türü (ör: code_review)
    :param prompt_text: Kaydedilecek prompt metni
    :return: İşlemin başarılı olup olmadığını belirten boolean değer
    """
    logger.info(f"{process_type} süreci için base prompt ekleniyor (varsa güncellenmeyecek).")
    try:
        db = get_db()
        collection_name = f"{process_type}_prompt"
        collection = db[collection_name]
        # Mevcut prompt'u ara
        existing = collection.find_one({"process_type": process_type})
        if existing:
            logger.warning(f"{process_type} için base prompt zaten mevcut, değiştirilmeyecek.")
            return False
        else:
            # Yeni prompt ekle
            result = collection.insert_one({
                "process_type": process_type,
                "prompt_text": prompt_text,
                "description": f"Base prompt for {process_type} process",
                "created_at": datetime.now()
            })
            success = result.acknowledged
        if success:
            logger.info(f"{process_type} süreci için base prompt başarıyla eklendi.")
        else:
            logger.warning(f"{process_type} süreci için base prompt eklenemedi.")
        return success
    except Exception as e:
        logger.error(f"Base prompt eklenirken hata oluştu: {str(e)}")
        return False

def get_code_review_system_suffix():
    """
    code_review_prompt koleksiyonundan system_suffix alanını döndürür.
    """
    logger.info("code_review system_suffix çekiliyor.")
    try:
        db = get_db()
        collection = db["code_review_prompt"]
        document = collection.find_one({"process_type": "code_review"})
        if document:
            return document.get("system_suffix", "\n\nCode to review:\n{code}")
        else:
            logger.warning("code_review için system_suffix bulunamadı, default değer döndürüldü.")
            return "\n\nCode to review:\n{code}"
    except Exception as e:
        logger.error(f"system_suffix çekilirken hata oluştu: {str(e)}")
        return "\n\nCode to review:\n{code}"

def get_requirement_analysis_system_suffix():
    """
    requirement_analysis_prompt koleksiyonundan system_suffix alanını döndürür.
    """
    logger.info("requirement_analysis system_suffix çekiliyor.")
    try:
        db = get_db()
        collection = db["requirement_analysis_prompt"]
        document = collection.find_one({"process_type": "requirement_analysis"})
        if document:
            return document.get("system_suffix", "\n\nCodebase:\n{code}\n\nRequirement Document:\n{requirement_document}")
        else:
            logger.warning("requirement_analysis için system_suffix bulunamadı, default değer döndürüldü.")
            return "\n\nCodebase:\n{code}\n\nRequirement Document:\n{requirement_document}"
    except Exception as e:
        logger.error(f"system_suffix çekilirken hata oluştu: {str(e)}")
        return "\n\nCodebase:\n{code}\n\nRequirement Document:\n{requirement_document}"



def get_test_planning_system_suffix():
    """
    test_planning_prompt koleksiyonundan system_suffix alanını döndürür.
    """
    logger.info("test_planning system_suffix çekiliyor.")
    try:
        db = get_db()
        collection = db["test_planning_prompt"]
        document = collection.find_one({"process_type": "test_planning"})
        if document:
            return document.get("system_suffix", "Test planning for the following:\nToday's date: {today}\nProject code:\n{code}\nRequirements document:\n{requirement_document}")
        else:
            logger.warning("test_planning için system_suffix bulunamadı, default değer döndürüldü.")
            return "Test planning for the following:\nToday's date: {today}\nProject code:\n{code}\nRequirements document:\n{requirement_document}"
    except Exception as e:
        logger.error(f"system_suffix çekilirken hata oluştu: {str(e)}")
        return "Test planning for the following:\nToday's date: {today}\nProject code:\n{code}\nRequirements document:\n{requirement_document}"



def get_environment_setup_system_suffix():
    logger.info("environment_setup system_suffix çekiliyor.")
    try:
        db = get_db()
        collection = db["environment_setup_prompt"]
        document = collection.find_one({"process_type": "environment_setup"})
        if document and document.get("system_suffix"):
            return document.get("system_suffix")
        else:
            logger.warning("environment_setup için system_suffix bulunamadı, default değer döndürüldü.")
            return (
                "Output Format:\n"
                "Don't make any explanation, just give the json structure. Otherwise, the program may crash, just give the json structure.\n"
                "You must output your result in JSON format with the following structure. The following is just an example. Fill in the variables according to the scheme, whatever should come in the files you throw in.:\n\n"
                "{{\n"
                "  \"environment_setup\": {{\n"
                "    \"language\": \"Python\",\n"
                "    \"language_version\": \">=3.9\",\n"
                "    \"framework\": \"Flask\",\n"
                "    \"operating_system\": \"Ubuntu 20.04\",\n"
                "    \"dependencies\": [\n"
                "      \"Flask==2.2.2\",\n"
                "      \"requests>=2.26\",\n"
                "      \"gunicorn>=20.1.0\"\n"
                "    ],\n"
                "    \"database\": \"Not Required\",\n"
                "    \"required_tools\": [\n"
                "      \"pip\",\n"
                "      \"virtualenv\"\n"
                "    ],\n"
                "    \"installation_notes\": \"...\"\n"
                "  }}\n"
                "}}\n\n"
                "Source Code:\n{code}\n"
                "Requirement Document:\n{requirement_document}"
            )
    except Exception as e:
        logger.error(f"system_suffix çekilirken hata oluştu: {str(e)}")
        return (
            "Output Format:\n"
            "Don't make any explanation, just give the json structure. Otherwise, the program may crash, just give the json structure.\n"
            "You must output your result in JSON format with the following structure. The following is just an example. Fill in the variables according to the scheme, whatever should come in the files you throw in.:\n\n"
            "{{\n"
            "  \"environment_setup\": {{\n"
            "    \"language\": \"Python\",\n"
            "    \"language_version\": \">=3.9\",\n"
            "    \"framework\": \"Flask\",\n"
            "    \"operating_system\": \"Ubuntu 20.04\",\n"
            "    \"dependencies\": [\n"
            "      \"Flask==2.2.2\",\n"
            "      \"requests>=2.26\",\n"
            "      \"gunicorn>=20.1.0\"\n"
            "    ],\n"
            "    \"database\": \"Not Required\",\n"
            "    \"required_tools\": [\n"
            "      \"pip\",\n"
            "      \"virtualenv\"\n"
            "    ],\n"
            "    \"installation_notes\": \"...\"\n"
            "  }}\n"
            "}}\n\n"
            "Source Code:\n{code}\n"
            "Requirement Document:\n{requirement_document}"
        )