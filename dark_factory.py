import os
import ollama

def run_dark_factory_batch():
    input_dir = "data"
    output_dir = "outputs"
    
    # Ensure folders exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if any txt files exist in data folder, if not create a default sample
    txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    if not txt_files:
        sample_file = os.path.join(input_dir, "meeting_transcript.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("# Project Kickoff Meeting\nHello team! Aaj ki meeting mein humein milestones decide karne hain aur AI model deployment ke tasks assign karne hain.")
        txt_files = ["meeting_transcript.txt"]
        
    print(f"[Dark Factory] Found {len(txt_files)} file(s) to process in '{input_dir}' folder.\n")
    
    for filename in txt_files:
        input_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{base_name}_report.md")
        
        print(f"----------------------------------------")
        print(f"Processing file: {filename}")
        print(f"----------------------------------------")
        
        with open(input_path, "r", encoding="utf-8") as f:
            transcript_data = f.read()
            
        # --- AGENT 1: The Creator ---
        print(" -> [Agent 1: Creator] Extracting key points and tasks...")
        creator_response = ollama.chat(model='gemma:2b', messages=[
            {
                'role': 'user',
                'content': f"Parse and chunk this meeting transcript into clean key points and actionable tasks:\n\n{transcript_data}",
            },
        ])
        creator_output = creator_response['message']['content']
        
        # --- AGENT 2: The Reviewer ---
        print(" -> [Agent 2: Reviewer] Refining format and adding priority tags...")
        reviewer_response = ollama.chat(model='gemma:2b', messages=[
            {
                'role': 'user',
                'content': f"Review the following meeting analysis. Fix any gaps, organize it cleanly with professional Markdown formatting, and add a priority tag (High/Medium/Low) to each task:\n\n{creator_output}",
            },
        ])
        final_output = reviewer_response['message']['content']
        
        # Save as structured Markdown report
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Dark Factory Intelligence Report\n\n**Source File:** `{filename}`\n\n---\n\n{final_output}")
            
        print(f" [Success] Saved report to {output_path}\n")

    print("=== All Batch Tasks Completed Successfully! ===")

if __name__ == "__main__":
    run_dark_factory_batch()