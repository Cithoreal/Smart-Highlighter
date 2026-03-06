topic_summary_prompt_json = (
        "You are an analyst.  You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Identify all main topics the user is exploring.  Return valid "
        "JSON in the form: [{ 'topic': str, 'description': str, "
        "'event_range': [start_id, end_id] }, ...]  "
        "Order the array by importance / user activity.  "
        "Always cite the smallest contiguous event_id range covering the topic."
)

selections_prompt_json = (
        " You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Identify all important text selections snippets the user has coppied.  Return valid "
        "JSON in the form: [{ 'selection': str,"
        "'event_range': [start_id, end_id] }, ...] "
        "Always cite the smallest contiguous event_id range covering the topic."
)

topic_summary_prompt_yaml = (
        "You are an analyst.  You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Identify all main topics the user is exploring.  Return valid "
        "YAML in the form: - topic: str\n  description: str\n  event_range: [start_id, end_id]\n"
        "Order the array by importance / user activity.  "
        "Always cite the smallest contiguous event_id range covering the topic."
)
behavior_insights_prompt_json = (
        "You are a data analyst.  You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Analyze the user behavior and provide insights based on the events.  "
        "Return valid JSON in the form: [{ 'insight': str, 'event_range': [start_id, end_id] }, ...]  "
        "Order the array by relevance and significance."
)

behavior_insights_prompt_yaml = (
        "You are a data analyst.  You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Analyze the user behavior and provide insights based on the events.  "
        "Return valid YAML in the form: - insight: str\n  event_range: [start_id, end_id]\n"
        "Order the array by relevance and significance."
)

actionable_steps_prompt_json = (
        "You are a data analyst.  You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Identify actionable steps based on the user's browsing behavior. Be imaginative and creative. Provide exciting and valuable recommendations.  "
        "Return valid JSON in the form: [{ 'step': str, 'event_range': [start_id, end_id] }, ...]  "
        "Order the array by priority and relevance."
)

# full_summary_prompt = (
#         "You are a technical writer.  Using the *topics* and *events* JSON "
#         "Begin the file by noting which model was used to generate the summary."
#         "below, create a structured table in markdown format with the following columns. First create a summary"
#         "of all of the main topics. There could be any number of main topics in the file. After you have all of the topics listed, go through each one and"
#         "create the table. If there has been no activity for over a minute, assume the user is inactive during the time on page. Write each cell with multiple"
#         "entries as bulleted lists. "
#         "Main topic: - Description: “What is the primary goal, intention, or topic the user is browsing for? Sort by timestamp"
#         "ascending of when a topic is first explored.” Sub topics: - Description: “What does the main topic break down into from the user’s activity?”"
#         "Behavior: - Description: “What insights can you interpret from the way the user is browsing this topic?” Data insights: - Description: “What insights"
#         "can you interpret from the data collected? ” Summaries of research: - Description: “Summarize all of the information collected from this topic.”"
#         "Selected text: - Description: “Copy important selections the user made exactly.” Ad traces: - Description: “Separate any ads or sponsors collected"
#         "while browsing this topic and collect them here  "
#         "When referencing evidence, cite event_id ranges in parentheses, e.g. "
#         "(events 233–271).  Finish with a bullet‑point recap of open questions "
#         "or next steps."
#     )

intro="""You are a technical writer using the *topics* and *events* JSON below, create a structured Markdown report.    
For each topic, include sub‑headings, behaviour analysis, ad traces, data insights, etc.  
When referencing evidence, cite event_id ranges in parentheses, e.g. (events 233–271).  
Finish with a bullet‑point recap of open questions or next steps. 



## Categories

### Topic:
Definition: Overall subject or theme of the user's browsing activity.
"""
description_a="""### Description:
Definition: A brief explanation of the topic, summarizing the user's intent or focus."""
description_b="""- Description: <Description of the topic>"""
selected_text_a="""### Selected Text
Description: Copy important selections and snippets the user made exactly."""
selected_text_b="""- Selected text <List all snippets for this topic completely, format code selections, and explain how this selected text fits into the context and what to do with it>"""
behavior_analysis_a="""### Behavior Analysis:
Definition: Insights derived from the user's interactions with the topic, including patterns, preferences, and engagement levels."""
behavior_analysis_b="""- Behavior Analysis: <Analysis of user behavior related to the topic>"""
data_insights_a="""### Data Insights:
Definition: Key findings or observations based on the data collected during the user's browsing, highlighting significant trends"""
data_insights_b="""- Data Insights: <Key findings from the data>"""
ad_traces_a="""### Ad Traces:
Definition: Any advertisements or sponsored content encountered while browsing the topic, including their relevance and impact on the user's experience."""
ad_traces_b="""- Ad Traces: <Details about ads or sponsored content encountered>"""
actionable_steps_a="""### Actionable Steps:
Definition: Based on the browsing activity, provide actionable steps or recommendations for the user to consider."""
actionable_steps_b="""- Actionable Steps: <Give actionable steps based on the insights generated on what to do or browse next>"""
second_section="""---

Examples: 

**Breakdown**
- Not informative: "The user drilled into ... repeatedly expanding and collapsing nodes ..."  
- Some information: "They focused on ... seeking confirmation of ..."  
    - First part is clear, but missing context as to what conversion the GPU is being used for. Audio to text? One audio format to another? Something else?  
"Questions about metadata retention during M4A→FLAC conversion prompted a brief “thought” pause before viewing a clean conversion snippet (events 1512–1514)."
    - Lots of missing context here. What does it mean by a 'brief "thought" pause? And in what context is there a clean conversation snippet?
- Excellent information: "Use of `<python snippet>` pattern ensures modularity and safety"

---

## How to respond
Return **markdown** exactly in the structure below:

```markdown
<Current LLM Model>
<Section Name> 
    
**Summary**

[Repeat for all topics in the file, using the following structure]
Topic X: <Topic Name>"""
def build_full_summary_prompt(options: dict) -> str:
    final_summary_prompt = intro
    
    if options.get("description"):
        final_summary_prompt += description_a + "\n\n"
    if options.get("selected_text"):
        final_summary_prompt += selected_text_a + "\n\n"   
    if options.get("behavior_analysis"):
        final_summary_prompt += behavior_analysis_a + "\n\n"
    if options.get("data_insights"):
        final_summary_prompt += data_insights_a + "\n\n"
    if options.get("ad_traces"):
        final_summary_prompt += ad_traces_a + "\n\n"
    if options.get("actionable_steps"):
        final_summary_prompt += actionable_steps_a + "\n\n"
        
    final_summary_prompt += second_section + "\n\n"
    
    if options.get("description"):
        final_summary_prompt += description_b + "\n"
    if options.get("selected_text"):
        final_summary_prompt += selected_text_b + "\n"
    if options.get("behavior_analysis"):
        final_summary_prompt += behavior_analysis_b + "\n"
    if options.get("data_insights"):
        final_summary_prompt += data_insights_b + "\n"
    if options.get("ad_traces"):
        final_summary_prompt += ad_traces_b + "\n"
    if options.get("actionable_steps"):
        final_summary_prompt += actionable_steps_b + "\n"

    return final_summary_prompt

full_summary_prompt = f"""
You are a technical writer using the *topics* and *events* JSON below, create a structured Markdown report.    
For each topic, include sub‑headings, behaviour analysis, ad traces, data insights, etc.  
When referencing evidence, cite event_id ranges in parentheses, e.g. (events 233–271).  
Finish with a bullet‑point recap of open questions or next steps. 



## Categories

### Topic:
Definition: Overall subject or theme of the user's browsing activity.

### Description:
Definition: A brief explanation of the topic, summarizing the user's intent or focus.

### Selected Text
Description: Copy important selections and snippets the user made exactly.

### Behavior Analysis:
Definition: Insights derived from the user's interactions with the topic, including patterns, preferences, and engagement levels.

### Data Insights:
Definition: Key findings or observations based on the data collected during the user's browsing, highlighting significant trends

### Ad Traces:
Definition: Any advertisements or sponsored content encountered while browsing the topic, including their relevance and impact on the user's experience.

### Actionable Steps:
Definition: The degree to which the insights generated can be acted upon or provide value to the user.

---

Examples: 

**Breakdown**
- Not informative: "The user drilled into ... repeatedly expanding and collapsing nodes ..."  
- Some information: "They focused on ... seeking confirmation of ..."  
    - First part is clear, but missing context as to what conversion the GPU is being used for. Audio to text? One audio format to another? Something else?  
"Questions about metadata retention during M4A→FLAC conversion prompted a brief “thought” pause before viewing a clean conversion snippet (events 1512–1514)."
    - Lots of missing context here. What does it mean by a 'brief "thought" pause? And in what context is there a clean conversation snippet?
- Excellent information: "Use of `<python snippet>` pattern ensures modularity and safety"

---

## How to respond
Return **markdown** exactly in the structure below:

```markdown
<Current LLM Model>
<Section Name> 
    
**Summary**

[Repeat for all topics in the file, using the following structure]
Topic X: <Topic Name>
- Description: <Description of the topic>
- Selected text <Explain how this selected text fits into the context and what to do with it>
- Behavior Analysis: <Analysis of user behavior related to the topic>
- Data Insights: <Key findings from the data>
- Ad Traces: <Details of any advertisements encountered>
- Actionable Steps: <How actionable or useful the insights are>
"""

final_report_prompt = """
You are a data analyst. You have recieved reports with tables and scores. Combine these reports into a single table that compares the scores of each report.
Finish with an analysis paragraph and note any notable details.
"""
topic_combination_prompt = """
You are recieving two json files. The first one is the current main topics sheet that is being maintained, and the second is a new topics sheet to be merged.
Rewrite the primary data and merge in the new data. Keep all data from both files and merge into a single file with all of the information.
Do not make up any new information. Do not discard any information.
For each main topic in the primary file, include subtopics that have been merged to create it. 
Continue to add to and maintain the descriptions of each topic as new data is merged
"""
behavior_combination_prompt = """
You are recieving two json files. The first one is a behavior analysis report being maintained, and the second is new behaviors sheet to be merged.
Rewrite the primary data and merge in the new data. Keep all data from both files and merge into a single file with all of the information.
Do not make up any new information. Do not discard any information.
For each main behavior in the primary file, include subbehaviors that have been merged to create it. 
Continue to add to and maintain the descriptions of each behavior as new data is merged
"""