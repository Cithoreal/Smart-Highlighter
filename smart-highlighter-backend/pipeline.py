# Data Flow
# Raw data gets saved to an input folder with any number of lateral subfolders from different tracking inputs. 
# Each with its own defined pipeline behavior
# If multiple pipelines exist for different flows, they will eventually get merged into a final full summary report
# This should be a class/scaffold script that each flow can build off of, starting with web-tracking data

class pipeline:
    
    # Contain all objects that will apply custom data processing to each layer of data. 
    # Sequential objects will process the outputs of the last objects and merge them
    # sibling objects will process the same information with different goals
    # The final object should merge all data process into a final report
    
    process_objects = []
    
    def pipeline(self):
        pass
    
    #
    def process_data_pipeline(self ):
        
        for data_process in self.process_objects:
            pass
            for sub_process in data_process:
                pass
    
    