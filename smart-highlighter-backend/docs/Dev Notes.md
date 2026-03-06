# 8/13/25

[ ] automatic self-signed certs for localhost https
[ ] Don't load LLM models if the api key isn't provided
[X] Give extension a remote and local host option













# 7/30/25
Latest git push was my work from before I got sick, forgot to push it before our last meeting

Going to focus on the tasks we described rather than focus on my goals at that time

X 1. A complete product (achievable from what you have)   
2. A report introducing the product and explaining to the customer how to use it. 
    a. Video of exploration => text dump => small summary => overview
    b. Narrative that includes some data about model choice, effectiveness of different ways of providing user data to customize summaries, etc.
3. A collection of 5+ benchmarks that show how it works and/or justify various design decisions.     
    a. Look up 'ablation'.  Run a scientific study on several different initial setups, and see which is best. 
    - Confused about ablation, but understand the instructions that follow
    b. Processing of raw data to end summaries 
x3        i. by model doing the summarizing (x5)
        ii. by prompt 
            1. wording (x3) [comment out in code]
            2. examples of what you like/don't like (x2)
                a. You need some way of providing information to the summarizer about what you want the output to look like.  Could be a user description/summary, could be examples, that's the hard creative decision.  THIS is where you will end up with lots of commented out stuff in the code (I see in git commits).  
X        iii. by data collected 
X            1. content viewed  (x3) 
X            2. data recorded  (same)
X            3. structure (yaml/json/ndjson) (x3)  [comment out in code]

## Goals

- [X] Compile tasks and show links from merged topics to original topics
- [X] chunk slide the entire raw log 
    - [X] main topics with edges to subtopics
    - [ ] behavior analysis report
    - [ ] llm as judge compiled scores

- [X] Change file timestamping to be windows friendly
- [X] Final Report
    - [X] Output all of the data scores into a single table to compare every configuration 

- [X] Chunking
    - [X] Sliding Chunking along the raw file to get three or more sets of data to process
    - [X] Test with different chunking sizes (10000, 20000, 30000)

- [X] Save three different filetypes for raw tracking data
    - [X] Change in plan, rather than dealing with three file, will just convert to data types from ndjson
    - [X] cache raw data in the pipeline so it can be referenced directly

    - ~~Load from each of the raw files~~
    - [X] Convert ndjson file to yaml and json to test all three
    - [X] ndjson 
    - [X] json
    - [X] yaml
- [X] Give all the information about models and prompts in the run to llm judge to include in the report
- [X] Run summarizing in the web_tracking_pipeline script (Hack it together rather than try to be clean)
    - [X] Run prompt options in parallel in a for loop
    - [X] Run model requests in parallel
    - [X] Run judge evaluation at the end of each (keep consistant)
    - [X] Note filename and pass it along to each step
- [X] Add connectors for other LLM options 
    - [X] Anthropic
    - [X] Hugging Face
    - [X] Google AI
    - [X] Collect API Keys for each service

- [ ] Take the multiple chunks of full summaries to generate a final comprehensive full summary.

- [ ] Use intermediary summaries to build data files
    - topics are simple - topic and description, updating them over time as more info is gained
    - behavior - Ask LLM to reference data and existing behavior file with the intention of building a behavior profile about the user
    - [X] metadata - Keeps track of the state of files, records event_ids that have been chunked and processed



# Next Steps 
- [X] Quality testing and reporting with GPT4.1
- [X]  the interface with gpt cleaner. Move LLM requests to its own script with the ability to pass in prompts and data freely 
- [ ] maintain a main topics json which lists every topic discovered by the summarizing systems. Add to this document and notes about this topic that can be referred to by user and AI 
- [ ] Maintain benchmark and rubric with annotations for good and bad responses
- [ ] Add batching option to GPT requests
- [ ] Add reasoning tool call options to GPT request

- [ ] Implement file text chunking
- [ ] Add a data archive folder. Once raw data has been chunked and pushed through the pipeline, remove it from the input file and add it to the archive file


# Report 
I have been implementing backend enhancements, working alongside ChatGPT

Topic and full summaries are automated to be generated on a timer. There is a very basic front end that displays topic and full summaries that have been created

Raw log file is now ndjson, so data can be appended and referenced without having to load the entire file text each time. It is also protected to be append and read only.


# Pipeline structure:

Raw Data -> Final Output

plugin processes that fit in automatically at any stage. Ordered and simultaneous. Each output saved, judged, and archived.

Main pipeline script that orchestrates how data gets processed. Judging is just another stage of data processing and outputing like everything else and does not need to be treated seperately in code.

# Batching

Batching takes individual lines from .jsonl files as the calls for batching, so for chunking, I need to process the entries in the .ndjson file and accumulate batches of roughly 6k-12k tokens (including the prompt itself) and create a new .jsonl object or file for processing. It's probably worth keeping all .jsonl files in an archive alongside the .ndjson raw data


