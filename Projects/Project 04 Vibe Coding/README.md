# Project 04 · Vibe Coding

This project introduces the use of AI coding assistants such as Codex to turn natural-language requirements into runnable programs through three hands-on tasks: construction-site image recognition, a personal academic website, and student learning data analysis.

## Before You Start

1. Install the Codex desktop app.
2. Sign in.
3. Send the corresponding prompt to the AI. Review the proposed plan first, then check the code and execution results.

## API: Connection Configuration Reference

### Files

| File | Purpose |
| --- | --- |
| `API.txt` | Existing instructions for using API keys |
| `auth.json` | Sample authentication file; keep it only on your local machine when in use |
| `config.toml` | Reference configuration for the model, service provider, API endpoint, and runtime options |

### Choose the Appropriate Connection Method

**Option A: Official OpenAI API.** Create a personal or project API key on the [OpenAI Platform], then use the API key sign-in option in Codex. Do not apply the repository's third-party configuration directly to the official OpenAI API.

**Option B: Third-Party Service Specified by the Course.** The current `config.toml` uses a custom provider named `codez` and points to a third-party endpoint. Before using it, confirm the endpoint, available models, API key, and billing rules with the course instructor. The model name and legacy options in the configuration are provided for reference and may not be supported by the current version.

## Project1: Construction-Site Image Recognition

### Objective

Use Python and a lightweight pretrained YOLO model to process a construction-site photograph, detect object classes supported by the model, draw bounding boxes, and summarize the number of detections for each class.

### Provided Materials

- `Construction.jpg`: Input image.
- `Prompt.txt`: Basic object detection task.
- `Next prompt.txt`: Follow-up training task for hard-hat and safety-vest detection.

## Project2: Personal Academic Website

### Objective

Work with the AI through conversation to organize your personal background and academic experience, then create a personal academic website suitable for both desktop and mobile viewing.

### Provided Materials

`Prompt.txt` offers two starting points:

- Create a website with About, Interests, Projects, Skills, Education, and Contact sections.
- Use the website referenced in the prompt as inspiration for the overall structure and presentation, then adapt the design to your own background.

## Project3: Student Learning Data Analysis

### Provided Materials

`student_learning.csv` contains 20 records with the following fields.

| Field | Meaning | Notes |
| --- | --- | --- |
| `student_id` | Student identifier 
| `study_hours` | Study time 
| `attendance_rate` | Attendance rate 
| `assignment_score` | Assignment score 
| `final_score` | Final exam score 
