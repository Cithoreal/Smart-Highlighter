# Looks over the latest summary files and writes a review and provides an overall score of its quality.
from typing import Optional
from llm_apis.llm_request import AI_API, make_llm_request
from storage import save_rubric_evaluation, _latest_file, get_full_summary, get_all_evaluations, get_evaluation_summary_sheet, get_topic_file_by_name, add_to_evaluation_sheet
import llm_judge.full_summary_rubric_examples
import llm_judge.full_summary_rubric_comparison
import llm_judge.topic_summary_rubric
import llm_judge.judge_output_rubric


#models = ["o4-mini"]
#models = ["gpt-4.1-2025-04-14", "o4-mini"]#, "gpt-4o-2024-08-06"]
#model = "gpt-4.1-2025-04-14"
#model = "o4-mini"
#model = "gpt-4o-2024-08-06"



def apply_rubric(original_prompt: str, summary_file: str, summaries_model: AI_API, notes: str = "",  llm_model: AI_API = AI_API.OPENAI_o4_mini, user_id: Optional[str] = None) -> str:
        print(f"Evaluating {summaries_model}")
        text_to_evaluate = get_full_summary(summary_file, user_id=user_id)
        if not text_to_evaluate:
            print(f"No text to evaluate at {summary_file}")
            return
        
        prompt_and_text = f"model: {summaries_model.value} \n other_details: {notes} \noriginal_prompt: {original_prompt} \n text_to_evaluate: {text_to_evaluate}"
        print(f"Prompt and text: {prompt_and_text}, llm_judge: {llm_judge.full_summary_rubric_comparison.get_rubric()}")  # Print first 500 characters for brevity
     
        #print(model, rubric, prompt_and_text)
        output = make_llm_request(prompt_and_text, llm_judge.full_summary_rubric_comparison.get_rubric(), llm_model)
        saved_file = save_rubric_evaluation(output, user_id=user_id)
        #print(f"Saved rubric evaluation to {saved_file}")
        return saved_file
        print ("Finished!")
        #return output

combined_prompt = "You are an expert data analyst and AI specialist. Your task is to merge two sets of notes into a single comprehensive summary. Focus on comparing the scores as you compare both sets of data"
def compile_scores(user_id: str):
    """Retrieve all topic summaries and one by one compare them to primary topics sheet, merging and expanding it"""
    
    #print(main_topics_sheet)
    for file in get_all_evaluations(user_id):
        main_topics_sheet = get_evaluation_summary_sheet(user_id)
        content = get_topic_file_by_name(file,user_id=user_id, directory="rubric_evaluations")
        if len(main_topics_sheet) == 0:
            add_to_evaluation_sheet(content, user_id)
        else:
            
            wrapped_data = f"Primary file: \n {main_topics_sheet} \n New data to merge:{content}"
            #print(wrapped_data)
            output = make_llm_request(combined_prompt, wrapped_data, AI_API.OPENAI_o4_mini)
            #print(output)
            add_to_evaluation_sheet(output, user_id)
            print("Gonna combine")
            #print("make llm request with prompt and both files")
            
        #For each file, compare it to the main topics file
        #if no main topics file, just copy the current file to start
        #Send both to llm with prompt to merge
        
        #print(content)
        
    
#apply_rubric()