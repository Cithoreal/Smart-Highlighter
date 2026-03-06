#from pipeline import pipeline
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from fastapi import logger
from summarizer import create_summary_json, create_summary_md
from llm_judge.llm_judge import apply_rubric, compile_scores
import logging
from llm_apis.llm_request import AI_API, make_llm_request
from chunking import chunk_and_record, get_whole_log
import json, ndjson, yaml
from storage import get_all_summary_type, get_topic_file_by_name, get_main_topics_summary_sheet, add_to_main_topics_summary_sheet, get_all_full_summaries
from web_tracking_prompts import (topic_summary_prompt_json, 
                                  selections_prompt_json,
                                  topic_combination_prompt, 
                                  topic_summary_prompt_yaml, 
                                  behavior_insights_prompt_json, 
                                  behavior_insights_prompt_yaml, 
                                  full_summary_prompt,
                                  actionable_steps_prompt_json,
                                  build_full_summary_prompt)
#Web pipe should look at the web tracking raw input file
#web_pipe = pipeline()


#web_pipe.process_objects = [create_topic_summary]

#process the entire raw web_tracking file in the input folder
#chunk it and move processed data into an archive file
#any time the file changes, check it and see if it's worth processing, based on how much data is accumulated and how long it has been sitting there
#primary information to get out of web tracking is the topics I am exploring, so extract topics into a central topics list json

#build on this topics json, appending new topics to it and adding to descriptions about what the topics are, maybe a history of each time the user 
#has looked it up.

#for each chunk processed, pull out an individual topics analysis. These files will be submitted to an LLM with the main topics file to be merged in.
#manage a version history that can be reviewed for this process. Maybe an implementation of git? backup all files onto github or an alternative?

#The other main interest is user insight. Have the llm review raw data for any general insights about user behavior and personality and maintain a main 
#file in the same way

#knowledge graph? linked topics? Auto tab grouping, saving, closing, and reopening?



# ------- PIPE --------
# Group lines from the web tracking file into batches of 6k-12k tokens as .jsonl files
# if there is less than 12k tokens in the file, then just process it as a single batch
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()  # This sends logs to the console
    ]
)
#logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
#logger = logging.getLogger(__name__)
#logger.addHandler(logging.StreamHandler(sys.stdout))  # Ensure logs are also printed to stdout

#Make things clean later

# Can externalize this or have variations as I test

#yaml_summary_prompts = [{"topics": topic_summary_prompt_yaml}, {"behavior": behavior_insights_prompt_yaml}]

### CUSTOMIZATION ###
#Middle Layer prompts
'''{"topics": topic_summary_prompt_json}, {"selections": selections_prompt_json}, {"behavior": behavior_insights_prompt_json}, {"actionable_steps": actionable_steps_prompt_json}}]'''
json_summary_prompts = [{"topics": topic_summary_prompt_json}, {"selections": selections_prompt_json}, {"behavior": behavior_insights_prompt_json}, {"actionable_steps": actionable_steps_prompt_json}]

#final_report_prompt options
full_summary_prompt_options = {"description": True, "selected_text": True, "behavior_analysis": True, "data_insights": True, "ad_traces": True, "actionable_steps": True}

#Models to use
#models=[AI_API.OPENAI_4o, AI_API.OPENAI_o4_mini, AI_API.ANTHROPIC, AI_API.GOOGLE]
models=[AI_API.GOOGLE]

def run_pipeline(user_id: Optional[str] = None):
    logging.debug(f"Running web tracking pipeline... User ID: {user_id}")
    """Run the web tracking pipeline to process raw events and generate summaries."""
    #Anthropic requires extra implementation when tokens exceed a certain amount, for now keep under 8000 total tokens
    reports = []
    i = 0
    #for chunk in tail_ndjson_sliding(chunk_tokens=5000, overlap_tokens=200, num_chunks=3):
    #    for report in run_models(chunk):
    #        reports.append({f"report_{i}": str(report)})
    #        i += 1
    raw_data = get_whole_log(user_id=user_id)
    report = run_models(raw_data, user_id=user_id)
    reports.append({"full_log": report})
    #for chunk in chunk_and_record(chunk_tokens=500, overlap_tokens=0, num_chunks=1, user_id=user_id):
    #    for report in run_models(chunk, user_id=user_id):
    #        reports.append({f"report_{i}": str(report)})
    #        i += 1

    # for chunk in tail_ndjson_sliding(chunk_tokens=10000, overlap_tokens=500, num_chunks=3):
    #     for report in run_models(chunk):
    #         reports.append({f"report_{i}": str(report)})
    #         i += 1
            
    # for chunk in tail_ndjson_sliding(chunk_tokens=20000, overlap_tokens=1000, num_chunks=3):
    #     for report in run_models(chunk):
    #         reports.append({f"report_{i}": str(report)})
    #         i += 1
    #full_summary_prompt = build_full_summary_prompt(full_summary_prompt_options)
    #create_summary_md(full_summary_prompt, reports, llm_model=AI_API.OPENAI_o4_mini, force=True, user_id=user_id)
        # build a full report llm request
def run_models(raw_data: str, user_id: Optional[str] = None) -> list[str]:
    logging.debug(f"Running models on raw data... User ID: {user_id}")
    reports = []
  
    for model in models:
        
        #Run json and yaml with no intermediate processing, just topics, and all
        #collect all of these and have an llm process them together
        #reports.append(run_pipeline_json([], raw_data, model, "JSON - No Intermediate Processing - raw data is NDJSON"))
        # reports.append(run_pipeline_json([topic_summary_prompt_json], raw_data, model, "JSON - Only Topics Preprocessed - raw data is NDJSON"))
        reports.append(run_pipeline_json(json_summary_prompts, raw_data, model, "JSON - topics, behavior insights Preprocessed - raw data is NDJSON", user_id=user_id))
        # reports.append(run_pipeline_json(json_summary_prompts, raw_data, model, "JSON - topics, behavior insights Preprocessed - raw data is JSON", json_format_raw=True))

        #reports.append(run_pipeline_yaml([], raw_data, model, "YAML - No Intermediate Processing - raw data is NDJSON"))
        # reports.append(run_pipeline_yaml([topic_summary_prompt_yaml], raw_data, model, "YAML - Only Topics Preprocessed - raw data is NDJSON"))
        # reports.append(run_pipeline_yaml(yaml_summary_prompts, raw_data, model, "YAML - topics, behavior insights Preprocessed - raw data is NDJSON"))
        # reports.append(run_pipeline_yaml(yaml_summary_prompts, raw_data, model, "YAML - topics, behavior insights Preprocessed - raw data is YAML", yaml_format_raw=True))
    return reports


        # build a full report llm request
def run_pipeline_json(summary_prompts: list[dict], raw_data: str, model=AI_API.OPENAI_o4_mini, json_format_raw:bool = False, notes: str = "", user_id: Optional[str] = None):
    """Run the web tracking pipeline to process raw events and generate summaries."""
    # Create a new topic summary from the raw data
    # raw data is a string of ndjson data
    logging.debug(f"Running web tracking pipeline (JSON)... User ID: {user_id}")
    if json_format_raw:
   
        raw_data = parse_ndjson(raw_data)
        if raw_data is None:
            logging.error("Failed to parse NDJSON data. Returning empty list.")
            return []

    try:
        logging.debug("Starting web tracking pipeline...")
        summary_files_list = []
        for summary_prompt in summary_prompts:
            summary_files_list.append({list(summary_prompt.keys())[0]: create_summary_json(summary_prompt, latest_events=raw_data, llm_model=model, force=True, user_id=user_id)})
        logging.debug(f"Topic summary completed. Saved to {summary_files_list}")
        # Create a full summary based on the latest topics and events
        full_summary_prompt = build_full_summary_prompt(full_summary_prompt_options)
        full_summary = create_summary_md(full_summary_prompt, summary_files_list, raw_data=raw_data, llm_model=model, force=True, user_id=user_id) #create_full_summary(full_summary_prompt, [topic_summary_path])
        logging.debug(f"Full summary completed. Saved to {full_summary}")
        rubric_file = apply_rubric(full_summary_prompt, full_summary, model, notes, user_id=user_id)
        print(f"Rubric evaluation applied to full summary. Saved to {rubric_file}")
        logging.debug(f"Rubric evaluation applied to full summary. Saved to {rubric_file}")
        return rubric_file
    except Exception as e:
        logging.exception(f"Error occurred while running pipeline: {e}")
        raise e

# def run_pipeline_yaml(summary_prompts: list[dict], raw_data: str, model=AI_API.OPENAI_o4_mini, yaml_format_raw:bool = False, notes: str = ""):
#     """Run the web tracking pipeline to process raw events and generate summaries in YAML format."""
#     # Create a new topic summary from the raw data
#     if yaml_format_raw:
#         parsed = parse_ndjson(raw_data)
#         raw_data = yaml.safe_load(yaml.dump(parsed))
#     try:
#         logging.debug("Starting web tracking pipeline (YAML)...")
        
#         summary_files_list = []
#         for summary_prompt in summary_prompts:
#             summary_files_list.append({list(summary_prompt.keys())[0]: create_summary_json(list(summary_prompt.values())[0], latest_events=raw_data, llm_model=model, force=True)})
#         logging.debug(f"Topic summary completed. Saved to {summary_files_list}")
#         # Create a full summary based on the latest topics and events
#         full_summary = create_summary_md(full_summary_prompt, summary_files_list, raw_data=raw_data, llm_model=model, force=True)
#         logging.debug(f"Full summary completed. Saved to {full_summary}")
#         rubric_file = apply_rubric(full_summary_prompt, full_summary, model, notes)
#         logging.debug(f"Rubric evaluation applied to full summary. Saved to {rubric_file}")
#         return rubric_file
#     except Exception as e:
#         logging.exception(f"Error occurred while running pipeline (YAML): {e}")
#         raise e
    

def create_topic_summary(force: bool = False, user_id: Optional[str] = None) -> str:
    """Create a topic summary from the latest raw events."""
    try:
        file = create_summary_json(topic_summary_prompt_json, llm_model=AI_API.OPENAI_o4_mini, force=force, user_id=user_id)
        return file
    except Exception as e:
        return f"Error creating topic summary: {e}"

def create_full_summary(prompt: str = full_summary_prompt, summary_list: list[str] = [create_topic_summary], force: bool = False) -> str:
    """Create a full summary from the latest raw events."""
    file = create_summary_md(prompt, summary_list, llm_model=AI_API.OPENAI_4o_mini, force=force)
    return file


def parse_ndjson(blob: str) -> list[dict]:
    if not isinstance(blob, str):
        raise ValueError("Input must be a string containing NDJSON data.")
    
    decoder = json.JSONDecoder()          # reuse for speed
    objs = []

    for lineno, line in enumerate(blob.splitlines(), start=1):
        txt = line.strip()
        if not txt:
            continue                      # skip blank lines

        try:
            objs.append(decoder.decode(txt))
        except json.JSONDecodeError as e:
            # Show a snippet so you can see *exactly* what broke
            logging.warning("Skipping malformed NDJSON (line %d): %s", lineno, e)
            
    return objs



def combine_topics(topic: str, user_id: str):
    """Retrieve all topic summaries and one by one compare them to primary topics sheet, merging and expanding it"""
    
    #print(main_topics_sheet)
    for file in get_all_full_summaries(topic, user_id):
        main_topics_sheet = get_main_topics_summary_sheet(topic, user_id)
        content = get_topic_file_by_name(file,user_id=user_id)
        if len(main_topics_sheet) == 0:
            add_to_main_topics_summary_sheet(topic, content, user_id)
        else:
            
            wrapped_data = f"Primary file: \n {main_topics_sheet} \n New data to merge:{content}"
            #print(wrapped_data)
            output = make_llm_request(topic_combination_prompt, wrapped_data, AI_API.OPENAI_o4_mini)
            #print(output)
            add_to_main_topics_summary_sheet(topic, output, user_id)
            print("Gonna combine")
            #print("make llm request with prompt and both files")
            
        #For each file, compare it to the main topics file
        #if no main topics file, just copy the current file to start
        #Send both to llm with prompt to merge
        
        #print(content)
        
def judge_reports(user_id: str, model: AI_API = AI_API.OPENAI_o4_mini):
    """Judge all reports for a user and compile scores."""
    logging.debug(f"Judging reports for user {user_id} with model {model.value}")
    
    # Apply rubric to each report
    for file in get_all_full_summaries(user_id):
        original_prompt = full_summary_prompt
        apply_rubric(original_prompt, file, model, user_id=user_id)


#REMEMBER TO REMOVE ANY LINES HERE BEFORE RUNNING THE SERVER

#judge_reports("Eval", model=AI_API.OPENAI_o4_mini)
#combine_topics("behavior", "Chris")
#compile_scores("Chris")

#print(build_full_summary_prompt(full_summary_prompt_options))

#can run the pipeline manually from here for testing
#run_pipeline("Eval")