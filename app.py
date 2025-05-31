
# code 6---------------------------------------------------------------------
# import os
# import time
# import threading
# import logging
# import sys
# import re
# import base64
# from datetime import datetime
# from PIL import ImageGrab, Image
# import pytesseract
# import google.generativeai as genai
# import requests

# # Configuration
# GEMINI_API_KEY = "AIzaSyCe_GBJsN9z9wCruEyKezHIPPZEkbGfv5Y"  # Your Gemini API key
# API_ENDPOINT = "https://message-web-4.onrender.com/messages"  # Correct endpoint
# API_KEY = "X7kP9mW3qT2rY8nF4vJ6hL5zB1cD"  # API key for message-web-4
# INTERVAL = 30
# SCREENSHOTS_DIR = "screenshots"
# RATE_LIMIT_BACKOFF = 60  # Wait 60 seconds if rate limited

# # Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.FileHandler("screenshot_monitor.log"), logging.StreamHandler(sys.stdout)]
# )

# # Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY)

# # Test API endpoint
# def test_api_endpoint():
#     try:
#         print("Testing API endpoint...")
#         payload = {"message": "Test message", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#         headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
#         response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
#         response.raise_for_status()
#         print(f"API endpoint test successful: {response.status_code}")
#         return True
#     except requests.exceptions.HTTPError as e:
#         print(f"API endpoint test failed: {e}, Status: {e.response.status_code}")
#         if e.response.status_code == 404:
#             print(f"Endpoint {API_ENDPOINT} not found. Verify the server is deployed and the endpoint is correct.")
#         elif e.response.status_code == 401:
#             print("Authentication failed. Verify the API key is correct.")
#         return False
#     except requests.exceptions.RequestException as e:
#         print(f"API endpoint test failed: {e}")
#         return False

# # Get available models
# def get_available_models():
#     try:
#         available_models = []
#         preferred_models = [
#             "models/gemini-1.5-flash",
#             "models/gemini-1.5-flash-latest",
#             "models/gemini-2.0-flash-lite",
#             "models/gemini-2.5-flash-preview"
#         ]
        
#         all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
#         logging.info(f"Available models: {all_models}")
        
#         for preferred in preferred_models:
#             for model in all_models:
#                 if preferred in model and "vision" not in model.lower() and "deprecated" not in model.lower():
#                     available_models.append(model)
#                     logging.info(f"Selected preferred model: {model}")
#                     break
        
#         if not available_models:
#             for model in all_models:
#                 if "vision" not in model.lower() and "deprecated" not in model.lower():
#                     available_models.append(model)
#                     logging.info(f"Selected fallback model: {model}")
        
#         return available_models
#     except Exception as e:
#         logging.error(f"Error listing models: {e}")
#         return []

# class ScreenshotMonitor:
#     def __init__(self, interval=30, screenshots_dir="screenshots"):
#         self.interval = interval
#         self.screenshots_dir = screenshots_dir
#         self.running = False
#         self.thread = None

#         if not os.path.exists(self.screenshots_dir):
#             os.makedirs(self.screenshots_dir)

#         try:
#             pytesseract.get_tesseract_version()
#             logging.info("Tesseract OCR is properly installed.")
#         except Exception as e:
#             logging.error(f"Tesseract OCR not found: {e}")
#             raise

#     def take_screenshot(self):
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filepath = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}.png")
#         try:
#             image = ImageGrab.grab()
#             image.save(filepath)
#             logging.info(f"Screenshot saved: {filepath}")
#             return filepath
#         except Exception as e:
#             logging.error(f"Error taking screenshot: {e}")
#             return None

#     def image_to_base64(self, image_path):
#         """Convert image to base64 string for API transmission"""
#         try:
#             with open(image_path, "rb") as image_file:
#                 encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
#                 return encoded_string
#         except Exception as e:
#             logging.error(f"Error converting image to base64: {e}")
#             return None

#     def compress_image_if_needed(self, image_path, max_size_mb=2):
#         """Compress image to ensure smaller payload size for API transmission"""
#         try:
#             # Check file size
#             file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            
#             # Always convert to JPEG for smaller size
#             compressed_path = image_path.replace('.png', '_compressed.jpg')
#             with Image.open(image_path) as img:
#                 # Calculate compression quality (75 or lower if needed)
#                 quality = min(75, max(20, int(75 - (file_size_mb - max_size_mb) * 15)))
#                 img.convert('RGB').save(compressed_path, 'JPEG', quality=quality, optimize=True)
                
#             compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
#             logging.info(f"Compressed image from {file_size_mb:.2f}MB to {compressed_size_mb:.2f}MB")
#             return compressed_path
            
#         except Exception as e:
#             logging.error(f"Error compressing image: {e}")
#             return image_path

#     def extract_text(self, image_path):
#         try:
#             img = Image.open(image_path)
#             text = pytesseract.image_to_string(img)
#             return text.strip()
#         except Exception as e:
#             logging.error(f"Error extracting text: {e}")
#             return ""

#     def is_meaningful_question(self, text):
#         """
#         Enhanced detection of meaningful questions with better code problem detection,
#         especially focusing on C++ requests
#         """
#         # Enhanced question detection
#         question_indicators = r'\b(what|why|how|when|where|who|which|can|could|should|would|is|are|does|do|solve|find|calculate|explain|write|create|implement|develop|design)\b'
#         has_question_mark = '?' in text
#         has_question_words = bool(re.search(question_indicators, text, re.IGNORECASE))
        
#         # Detect code-related queries - expanded keywords
#         code_indicators = r'\b(code|program|function|class|algorithm|implementation|c\+\+|cpp|python|java|javascript|algorithm|solution|problem|challenge|leetcode|coding|codeforces|hackerrank|programming|assignment|project|task|exercise|homework|development|software|application|implement|develop|write a|create a)\b'
#         has_code_keywords = bool(re.search(code_indicators, text, re.IGNORECASE))
        
#         # Common programming tasks - expanded patterns
#         code_tasks = r'\b(write|create|develop|implement|design|build|code|program|solve|fix|debug|optimize)\b.{1,70}\b(function|program|method|algorithm|solution|problem|code|program|application|system)\b'
#         is_code_task = bool(re.search(code_tasks, text, re.IGNORECASE))
        
#         # Check for C++ specific requests - improved detection
#         cpp_indicators = r'\b(c\+\+|cpp|c plus plus|in c\+\+|using c\+\+|with c\+\+|c\+\+ program|c\+\+ code|c\+\+ implementation|c\++/solution|c\+\+ algorithm|c\+\+ class|c\+\+ function)\b'
#         is_cpp_request = bool(re.search(cpp_indicators, text, re.IGNORECASE))
        
#         # Additional pattern to detect when someone wants a solution in C++
#         cpp_solution_request = bool(re.search(r'\b(solution|code|program|implementation|algorithm).{1,20}(in|using|with) c\+\+\b', text, re.IGNORECASE))
#         if cpp_solution_request:
#             is_cpp_request = True
        
#         # Detect programming problem patterns
#         programming_patterns = [
#             r'given an (array|input|integer|string|vector|list|graph|tree)',
#             r'write a (function|program|method|algorithm)',
#             r'implement a (function|program|method|algorithm)',
#             r'create a (function|program|method|algorithm)',
#             r'find the (maximum|minimum|average|sum|product|median)',
#             r'time complexity.*space complexity',
#             r'return the (result|output|answer|value)',
#             r'O\(n\)|O\(n²\)|O\(n log n\)|O\(1\)',
#         ]
#         has_programming_pattern = any(bool(re.search(pattern, text, re.IGNORECASE)) for pattern in programming_patterns)
        
#         # Check for input/output examples which often appear in programming problems
#         io_example_pattern = r'(input|example|test case).*?:\s*.*?\s*(output|result).*?:'
#         has_io_example = bool(re.search(io_example_pattern, text, re.IGNORECASE | re.DOTALL))
        
#         # If any programming pattern is found, consider it a coding problem
#         is_coding_problem = has_programming_pattern or has_io_example or is_code_task
        
#         # If it's a coding problem but no specific language is mentioned, assume C++ by default
#         if is_coding_problem and not is_cpp_request:
#             # Check if another language is explicitly requested
#             other_languages = r'\b(python|java|javascript|typescript|golang|ruby|rust|swift|php|c#)\b'
#             if not bool(re.search(other_languages, text, re.IGNORECASE)):
#                 # No other language specified, default to C++
#                 is_cpp_request = True
#                 logging.info("Coding problem detected with no specific language, defaulting to C++")
        
#         # Regular text questions with enough substance (at least 20 chars)
#         meaningful_text_question = has_question_mark and len(text) > 20
        
#         # Combine factors for decision
#         is_meaningful = (has_question_words and (len(text) > 20)) or \
#                        has_code_keywords or \
#                        is_code_task or \
#                        is_cpp_request or \
#                        is_coding_problem or \
#                        has_programming_pattern or \
#                        has_io_example or \
#                        meaningful_text_question
                       
#         logging.info(f"Question analysis: has_question_mark={has_question_mark}, has_question_words={has_question_words}, " 
#                      f"has_code_keywords={has_code_keywords}, is_code_task={is_code_task}, is_cpp_request={is_cpp_request}, "
#                      f"is_coding_problem={is_coding_problem}, has_programming_pattern={has_programming_pattern}, "
#                      f"decision={is_meaningful}")
        
#         return is_meaningful, is_cpp_request

#     def format_response(self, response, is_code_response=False):
#         """
#         Improved formatting of the Gemini response for better readability,
#         with special handling for C++ code.
#         """
#         if not response:
#             return "No response received from AI model."
        
#         # If it's already well-formatted, return as is
#         if "```" in response or "###" in response:
#             # Make sure C++ code is properly tagged
#             if is_code_response and "```cpp" not in response and "```c++" not in response:
#                 response = response.replace("```", "```cpp", 1)
#             return response
            
#         # Check if this appears to be a code solution
#         code_block_start = re.search(r'(Here\'s|This is|The|A) (the )?(complete |full )?(code|solution|implementation|program)', response, re.IGNORECASE)
        
#         if is_code_response or code_block_start:
#             # Try to identify the code portion and wrap it in markdown
#             code_lines = []
#             explanation_lines = []
#             in_code_block = False
            
#             lines = response.split('\n')
#             for i, line in enumerate(lines):
#                 # Detect start of code block - enhanced for C++
#                 if not in_code_block and (
#                     code_block_start and i >= code_block_start.start() or
#                     line.strip().startswith('#include') or 
#                     line.strip().startswith('using namespace') or
#                     line.strip().startswith('int main') or
#                     line.strip().startswith('class ') or
#                     line.strip().startswith('struct ') or  # Added for C++ struct
#                     line.strip().startswith('template<') or  # Added for C++ templates
#                     line.strip().startswith('void ') or  # Common C++ function return type
#                     line.strip().startswith('int ') or  # Common C++ function return type
#                     line.strip().startswith('bool ') or  # Common C++ function return type
#                     line.strip().startswith('string ') or  # Common C++ function return type
#                     line.strip().startswith('vector<') or  # Common C++ container
#                     line.strip().startswith('def ') or
#                     line.strip().startswith('public class') or
#                     line.strip().startswith('// ') or
#                     line.strip().startswith('/*')
#                 ):
#                     explanation_lines.extend(lines[:i])
#                     in_code_block = True
#                     code_lines.append(line)
#                 elif in_code_block:
#                     code_lines.append(line)
            
#             # If we identified code properly
#             if code_lines:
#                 explanation_text = '\n'.join(explanation_lines).strip()
#                 code_text = '\n'.join(code_lines).strip()
                
#                 # Determine the language with improved C++ detection
#                 lang = "cpp" if (
#                     is_code_response or  # If we already detected C++ request
#                     any(cpp_keyword in code_text for cpp_keyword in [
#                         '#include', 'using namespace std', 'int main', 'cout', 'cin', 
#                         'vector<', 'std::', '::iterator', '->', 'nullptr', 'template<',
#                         'auto ', 'const ', 'void ', 'bool ', 'static_cast<'
#                     ])
#                 ) else "python"
                
#                 formatted_response = explanation_text + "\n\n```" + lang + "\n" + code_text + "\n```"
#                 return formatted_response.strip()
        
#         # If it's not code or we couldn't properly format it, return with minimal formatting
#         paragraphs = re.split(r'\n\s*\n', response)
#         formatted_paragraphs = []
        
#         for para in paragraphs:
#             # Check if this paragraph contains a heading-like text
#             if re.match(r'^[A-Z][A-Za-z\s]+:$', para.strip()) or para.strip().isupper():
#                 formatted_paragraphs.append(f"### {para.strip()}")
#             else:
#                 formatted_paragraphs.append(para.strip())
                
#         return "\n\n".join(formatted_paragraphs)

#     def clean_response(self, response):
#         """Remove unnecessary parts of the response to make it more concise."""
#         # Remove standard disclaimers
#         cleaned = re.sub(r"I'm an AI (assistant|model).*?knowledge cutoff.*?\.", "", response, flags=re.DOTALL|re.IGNORECASE)
#         cleaned = re.sub(r"As an AI (assistant|model).*?knowledge cutoff.*?\.", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
        
#         # Remove "I'd be happy to help" type phrases
#         cleaned = re.sub(r"(I'd be happy to|I'd be glad to|I can certainly|Let me|Here's|I'll|I will) (help|assist|provide|create|write|solve|answer).*?\.", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
        
#         # Remove "I hope this helps" and similar phrases at the end
#         cleaned = re.sub(r"(I hope this helps|Let me know if you need any clarification|If you have any questions).*$", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
        
#         # Fix multiple blank lines
#         cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        
#         return cleaned.strip()

#     def send_to_api(self, response, image_path=None):
#         """Send the Gemini response and screenshot to the specified API endpoint."""
#         try:
#             payload = {
#                 "message": response,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
            
#             # Add screenshot if available
#             if image_path and os.path.exists(image_path):
#                 # Compress image if needed
#                 compressed_path = self.compress_image_if_needed(image_path)
                
#                 # Convert to base64
#                 image_base64 = self.image_to_base64(compressed_path)
#                 if image_base64:
#                     payload["screenshot"] = {
#                         "data": image_base64,
#                         "format": "image/jpeg" if compressed_path.endswith('.jpg') else "image/png",
#                         "filename": os.path.basename(compressed_path)
#                     }
#                     logging.info("Screenshot added to payload")
                
#                 # Clean up compressed file if it's different from original
#                 if compressed_path != image_path and os.path.exists(compressed_path):
#                     try:
#                         os.remove(compressed_path)
#                     except:
#                         pass
            
#             headers = {
#                 "Content-Type": "application/json",
#                 "x-api-key": API_KEY
#             }
            
#             api_response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=30)  # Increased timeout for image upload
#             api_response.raise_for_status()
#             logging.info(f"Successfully sent response with screenshot to API: {api_response.status_code}")
#             return api_response.json() if api_response.content else {"status": "success"}
            
#         except requests.exceptions.HTTPError as e:
#             logging.error(f"HTTP error sending response to API: {e}, Status: {e.response.status_code}")
#             try:
#                 error_details = e.response.json()
#             except ValueError:
#                 error_details = e.response.text
#             return {"error": str(e), "status_code": e.response.status_code, "details": error_details}
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Error sending response to API: {e}")
#             return {"error": str(e)}

#     def get_gemini_response(self, text, is_cpp_request=False):
#         """
#         Improved prompt engineering for getting better C++ responses from Gemini
#         """
#         try:
#             available_models = get_available_models()
            
#             if not available_models:
#                 return "No Gemini models are available. Please check your API key and quotas."
            
#             errors = []
#             for model_name in available_models[:3]:
#                 try:
#                     logging.info(f"Attempting to use model: {model_name}")
#                     model = genai.GenerativeModel(model_name)
                    
#                     if is_cpp_request:
#                         # Enhanced C++ prompt with better instructions
#                         prompt = (
#                             f"The following text appears to contain a C++ coding problem or request:\n\n{text}\n\n"
#                             f"You MUST provide a complete and professional C++ solution with the following structure:\n"
#                             f"1. A brief explanation of the approach and algorithm\n"
#                             f"2. The full, well-commented C++ code that solves the problem\n"
#                             f"3. Include all necessary headers (e.g., iostream, vector, string, etc.)\n"
#                             f"4. Use proper namespace declarations (using namespace std;)\n"
#                             f"5. Make sure the main() function is complete and demonstrates usage\n"
#                             f"6. Include test cases or example inputs/outputs where appropriate\n"
#                             f"7. Ensure the code is complete, efficient, and follows C++ best practices\n"
#                             f"8. Use modern C++ features when appropriate (C++11/14/17 features)\n"
#                             f"The code must be directly compilable without any modifications.\n"
#                             f"Do not include apologies, disclaimers or statements about your capabilities."
#                         )
#                     else:
#                         # General programming prompt
#                         prompt = (
#                             f"The following text appears to contain a question or a programming problem:\n\n{text}\n\n"
#                             f"Provide a complete and detailed solution to the question or problem. "
#                             f"If it's a coding problem, include the full code with explanations. "
#                             f"If it's a textual question, provide a comprehensive answer with clear reasoning. "
#                             f"Be concise and avoid unnecessary apologies or disclaimers."
#                         )
                    
#                     max_retries = 2
#                     backoff_time = RATE_LIMIT_BACKOFF
                    
#                     for attempt in range(max_retries):
#                         try:
#                             response = model.generate_content(prompt)
#                             logging.info(f"Successfully used model {model_name}")
#                             raw_response = response.text.strip()
                            
#                             # Clean and format the response
#                             cleaned_response = self.clean_response(raw_response)
#                             formatted_response = self.format_response(cleaned_response, is_cpp_request)
                            
#                             # Double check for C++ code - if requested but not provided
#                             if is_cpp_request and "```cpp" not in formatted_response and "#include" not in formatted_response:
#                                 logging.warning("C++ solution was requested but not detected in response. Retrying with more explicit prompt.")
#                                 # Retry with more explicit C++ instructions
#                                 cpp_rescue_prompt = (
#                                     f"IMPORTANT: You MUST provide a C++ solution for this problem:\n\n{text}\n\n"
#                                     f"Write ONLY C++ code that includes:\n"
#                                     f"1. All necessary headers (#include statements)\n"
#                                     f"2. Namespace declaration (using namespace std;)\n"
#                                     f"3. A complete main() function\n"
#                                     f"4. Full implementation of all required functions/classes\n"
#                                     f"The solution must be in C++ ONLY, not any other language. Your response should start with #include statements."
#                                 )
#                                 retry_response = model.generate_content(cpp_rescue_prompt)
#                                 retry_raw = retry_response.text.strip()
#                                 retry_cleaned = self.clean_response(retry_raw)
#                                 retry_formatted = self.format_response(retry_cleaned, True)
                                
#                                 # Check if we now have C++ code
#                                 if "```cpp" in retry_formatted or "#include" in retry_formatted:
#                                     logging.info("Successfully retrieved C++ solution on retry")
#                                     return retry_formatted
#                                 else:
#                                     # Still no C++ code, continue with original response
#                                     logging.warning("Failed to get C++ code even with explicit retry")
                            
#                             return formatted_response
#                         except Exception as retry_error:
#                             if "429" in str(retry_error) and attempt < max_retries - 1:
#                                 logging.warning(f"Rate limited. Waiting {backoff_time} seconds before retry...")
#                                 time.sleep(backoff_time)
#                                 backoff_time *= 2
#                             else:
#                                 raise
#                 except Exception as model_error:
#                     errors.append(f"{model_name}: {str(model_error)}")
#                     logging.warning(f"Model {model_name} failed: {str(model_error)}")
#                     continue
            
#             error_msg = "All Gemini models failed. Errors:\n" + "\n".join(errors)
#             logging.error(error_msg)
#             return "Failed to get response from any AI model. You may have exceeded your quota limits or the models may be unavailable."
            
#         except Exception as e:
#             logging.error(f"Error getting Gemini response: {e}")
#             return f"Gemini API Error: {str(e)}. You may have exceeded your quota limits."

#     def detect_coding_problem_type(self, text):
#         """
#         Advanced detection to determine if a text likely contains a coding problem
#         and what language is preferred or required.
#         """
#         # Check for explicit C++ mentions
#         cpp_indicators = r'\b(c\+\+|cpp|c plus plus|in c\+\+|using c\+\+|with c\+\+)\b'
#         is_cpp_explicit = bool(re.search(cpp_indicators, text, re.IGNORECASE))
        
#         # Check for implicit C++ indicators (common C++ syntax/keywords)
#         cpp_implicit = any(keyword in text for keyword in [
#             'iostream', '#include', 'cin>>', 'cout<<', 'namespace std', 'vector<', 
#             'std::', '::iterator', 'nullptr', 'template<', 'constexpr'
#         ])
        
#         # Check for other language indicators
#         python_indicators = r'\b(python|\.py|def |import |from \w+ import)\b'
#         java_indicators = r'\b(java|public class|public static void main)\b'
#         js_indicators = r'\b(javascript|js|node\.js|const |let |function\s+\w+$$  $$)\b'
        
#         is_python = bool(re.search(python_indicators, text, re.IGNORECASE))
#         is_java = bool(re.search(java_indicators, text, re.IGNORECASE))
#         is_javascript = bool(re.search(js_indicators, text, re.IGNORECASE))
        
#         # Check if it appears to be a coding problem
#         code_problem_indicators = [
#             r'implement (a|an|the) (function|algorithm|solution)',
#             r'write (a|an|the) (function|algorithm|program)',
#             r'time complexity',
#             r'given an (array|string|integer|vector|list|input)',
#             r'find the (maximum|minimum|sum|average|median)',
#             r'return the (result|answer|output)',
#             r'example input.*example output',
#             r'test case',
#             r'problem statement',
#             r'leetcode|hackerrank|codeforces'
#         ]
        
#         is_coding_problem = any(bool(re.search(pattern, text, re.IGNORECASE)) for pattern in code_problem_indicators)
        
#         # Determine the likely language
#         if is_cpp_explicit or cpp_implicit:
#             return is_coding_problem, True  # It's a C++ request
#         elif is_python or is_java or is_javascript:
#             return is_coding_problem, False  # It's a coding problem but not C++
#         elif is_coding_problem:
#             # It's a coding problem with no specific language - default to C++
#             return True, True
#         else:
#             return False, False  # Not a coding problem

#     def process_screenshot(self):
#         path = self.take_screenshot()
#         if not path:
#             return

#         text = self.extract_text(path)
#         if not text:
#             logging.warning("No text found in screenshot.")
#             return

#         # Enhanced detection for coding problems
#         is_coding_problem, is_cpp_default = self.detect_coding_problem_type(text)
        
#         # Standard question detection as backup
#         is_meaningful, is_cpp_explicit = self.is_meaningful_question(text)
        
#         # Combine results for best detection
#         is_cpp_request = is_cpp_explicit or (is_coding_problem and is_cpp_default)
        
#         if not is_meaningful and not is_coding_problem:
#             logging.info("No meaningful question or coding problem detected in screenshot. Skipping.")
#             return
            
#         # Log what was detected
#         if is_coding_problem:
#             logging.info(f"Coding problem detected. Is C++ requested: {is_cpp_request}")
#         else:
#             logging.info(f"Meaningful question detected. Is C++ requested: {is_cpp_request}")
            
#         # Get response from Gemini
#         response = self.get_gemini_response(text, is_cpp_request)

#         # Send response and screenshot to API
#         api_result = self.send_to_api(response, path)
        
#         # Display the Gemini response and API result
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         print(f"\n=== SCREENSHOT ANALYSIS ({timestamp}) ===\n")
        
#         if is_cpp_request:
#             print(f"Detected: Coding problem requiring C++ solution")
#         elif is_coding_problem:
#             print(f"Detected: Coding problem (general)")
#         else:
#             print(f"Detected: Meaningful question")
            
#         print(f"\nGemini Response:\n{response}\n")
#         print(f"API Response:\n{api_result}\n")

#     def _monitor_loop(self):
#         while self.running:
#             try:
#                 self.process_screenshot()
#                 time.sleep(self.interval)
#             except Exception as e:
#                 logging.error(f"Loop error: {e}")
#                 time.sleep(5)

#     def start(self):
#         if self.running:
#             print("Monitor already running.")
#             return
#         self.running = True
#         self.thread = threading.Thread(target=self._monitor_loop)
#         self.thread.daemon = True
#         self.thread.start()
#         print("Screenshot monitor started.")

#     def stop(self):
#         self.running = False
#         if self.thread:
#             self.thread.join()
#         print("Screenshot monitor stopped.")

# def test_gemini_connection():
#     try:
#         print("Testing Gemini API connection...")
#         available_models = get_available_models()
        
#         if not available_models:
#             print("No models available for content generation. Check your API key and permissions.")
#             return False
        
#         model_name = available_models[0]
#         print(f"Testing with available model: {model_name}")
#         model = genai.GenerativeModel(model_name)
#         response = model.generate_content("Test")
#         print(f"Gemini API connection successful with model {model_name}!")
#         return True
#     except Exception as e:
#         print(f"Gemini API connection test failed: {e}")
#         return False

# def main():
#     """Main function to run the screenshot monitor"""
#     print("Screenshot Monitor with AI Analysis")
#     print("===================================")
    
#     # Test API endpoint first
#     if not test_api_endpoint():
#         print("API endpoint test failed. Please check your configuration.")
#         return
    
#     # Test Gemini connection
#     if not test_gemini_connection():
#         print("Gemini API test failed. Please check your API key and quotas.")
#         return
    
#     # Initialize and start the monitor
#     monitor = ScreenshotMonitor(interval=INTERVAL, screenshots_dir=SCREENSHOTS_DIR)
    
#     try:
#         monitor.start()
#         print(f"Monitor is running. Taking screenshots every {INTERVAL} seconds.")
#         print("Press Ctrl+C to stop the monitor.")
        
#         # Keep the main thread alive
#         while True:
#             time.sleep(1)
            
#     except KeyboardInterrupt:
#         print("\nShutdown signal received...")
#         monitor.stop()
#         print("Screenshot monitor has been stopped.")
#     except Exception as e:
#         logging.error(f"Unexpected error in main: {e}")
#         monitor.stop()

# if __name__ == "__main__":
#     main()
# code 5-------------------------------------
# import os
# import time
# import threading
# import logging
# import sys
# import re
# from datetime import datetime
# from PIL import ImageGrab, Image
# import pytesseract
# import google.generativeai as genai
# import requests
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import threading
# from pyngrok import ngrok
# # Move this line up, right after the imports and before any route definitions
# app = Flask(__name__)
# CORS(app, resources={r"/take-screenshot": {"origins": ["*"]}})  # Allow all origins for ngrok tunnel

# # ADD THESE LINES HERE:
# @app.route('/test', methods=['GET'])  
# def test_endpoint():
#     logging.info("Test endpoint called")
#     return jsonify({"status": "Flask server is running with ngrok"}), 200

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({
#         "status": "Screenshot API is running", 
#         "endpoints": ["/test", "/take-screenshot"],
#         "message": "Use ngrok tunnel URL to access this API"
#     }), 200
# # Configuration
# GEMINI_API_KEY = "AIzaSyCe_GBJsN9z9wCruEyKezHIPPZEkbGfv5Y"  # Replace with your Gemini API key
# API_ENDPOINT = "https://message-web-4.onrender.com/messages"  # Your API endpoint
# API_KEY = "X7kP9mW3qT2rY8nF4vJ6hL5zB1cD"  # Your API key for message-web-4
# INTERVAL = 30  # Seconds between screenshots
# SCREENSHOTS_DIR = "screenshots"  # Directory for screenshots (relative to .exe)
# RATE_LIMIT_BACKOFF = 60  # Wait 60 seconds if rate limited
# # # Flask app for API endpoint
# # app = Flask(__name__)

# # Set Tesseract path (adjust if Tesseract is installed elsewhere)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # Setup logging to file only (no console for background .exe)
# log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot_monitor.log")
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.FileHandler(log_file),
#               logging.StreamHandler(sys.stdout)
#               ]
# )

# # Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY)

# # Test API endpoint
# def test_api_endpoint():
#     try:
#         logging.info("Testing API endpoint...")
#         payload = {"message": "Test message", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#         headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
#         response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
#         response.raise_for_status()
#         logging.info(f"API endpoint test successful: {response.status_code}")
#         return True
#     except requests.exceptions.HTTPError as e:
#         logging.error(f"API endpoint test failed: {e}, Status: {e.response.status_code}")
#         if e.response.status_code == 404:
#             logging.error(f"Endpoint {API_ENDPOINT} not found. Verify the server is deployed and the endpoint is correct.")
#         elif e.response.status_code == 401:
#             logging.error("Authentication failed. Verify the API key is correct.")
#         return False
#     except requests.exceptions.RequestException as e:
#         logging.error(f"API endpoint test failed: {e}")
#         return False
# #     # for taking screen shot
# # @app.route('/take-screenshot', methods=['POST'])
# # def trigger_screenshot():
# #     """API endpoint to trigger screenshot on demand"""
# #     try:
# #         # Verify API key if needed
# #         api_key = request.headers.get('x-api-key')
# #         if api_key != API_KEY:
# #             return jsonify({"error": "Invalid API key"}), 401
        
# #         # Create monitor instance and process screenshot
# #         monitor = ScreenshotMonitor(interval=INTERVAL, screenshots_dir=SCREENSHOTS_DIR)
# #         monitor.process_screenshot()
        
# #         return jsonify({"status": "Screenshot processed successfully"}), 200
# #     except Exception as e:
# #         logging.error(f"Error processing screenshot request: {e}")
# #         return jsonify({"error": str(e)}), 500
# # # Get available models
# def get_available_models():
#     try:
#         available_models = []
#         preferred_models = [
#             "models/gemini-1.5-flash",
#             "models/gemini-1.5-flash-latest",
#             "models/gemini-2.0-flash-lite",
#             "models/gemini-2.5-flash-preview"
#         ]
        
#         all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
#         logging.info(f"Available models: {all_models}")
        
#         for preferred in preferred_models:
#             for model in all_models:
#                 if preferred in model and "vision" not in model.lower() and "deprecated" not in model.lower():
#                     available_models.append(model)
#                     logging.info(f"Selected preferred model: {model}")
#                     break
        
#         if not available_models:
#             for model in all_models:
#                 if "vision" not in model.lower() and "deprecated" not in model.lower():
#                     available_models.append(model)
#                     logging.info(f"Selected fallback model: {model}")
        
#         return available_models
#     except Exception as e:
#         logging.error(f"Error listing models: {e}")
#         return []

# class ScreenshotMonitor:
#     def __init__(self, interval=30, screenshots_dir="screenshots"):
#         self.interval = interval
#         self.screenshots_dir = screenshots_dir

#         # Create screenshots directory if it doesn't exist
#         if not os.path.exists(self.screenshots_dir):
#             try:
#                 os.makedirs(self.screenshots_dir)
#                 logging.info(f"Created screenshots directory: {self.screenshots_dir}")
#             except Exception as e:
#                 logging.error(f"Failed to create screenshots directory: {e}")
#                 raise

#         # Verify Tesseract installation
#         try:
#             pytesseract.get_tesseract_version()
#             logging.info("Tesseract OCR is properly installed.")
#         except Exception as e:
#             logging.error(f"Tesseract OCR not found: {e}")
#             raise

#     def take_screenshot(self):
#         logging.info("Taking screenshot...")
#         logging.info(f"Screenshots directory: {self.screenshots_dir}")
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filepath = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}.png")
#         logging.info(f"Screenshot will be saved to: {filepath}")
#         try:
#             image = ImageGrab.grab()
#             image.save(filepath)
#             logging.info(f"Screenshot saved: {filepath}")
#             return filepath
#         except Exception as e:
#             logging.error(f"Error taking screenshot: {e}")
#             return None

#     def extract_text(self, image_path):
#         try:
#             img = Image.open(image_path)
#             text = pytesseract.image_to_string(img)
#             return text.strip()
#         except Exception as e:
#             logging.error(f"Error extracting text: {e}")
#             return ""

#     def is_meaningful_question(self, text):
#         """
#         Enhanced detection of meaningful questions with better code problem detection,
#         especially focusing on C++ requests.
#         """
#         question_indicators = r'\b(what|why|how|when|where|who|which|can|could|should|would|is|are|does|do|solve|find|calculate|explain|write|create|implement|develop|design)\b'
#         has_question_mark = '?' in text
#         has_question_words = bool(re.search(question_indicators, text, re.IGNORECASE))
        
#         code_indicators = r'\b(code|program|function|class|algorithm|implementation|c\+\+|cpp|python|java|javascript|algorithm|solution|problem|challenge|leetcode|coding|codeforces|hackerrank|programming|assignment|project|task|exercise|homework|development|software|application|implement|develop|write a|create a)\b'
#         has_code_keywords = bool(re.search(code_indicators, text, re.IGNORECASE))
        
#         code_tasks = r'\b(write|create|develop|implement|design|build|code|program|solve|fix|debug|optimize)\b.{1,70}\b(function|class|method|program|algorithm|solution|problem|code|program|application|system)\b'
#         is_code_task = bool(re.search(code_tasks, text, re.IGNORECASE))
        
#         cpp_indicators = r'\b(c\+\+|cpp|c plus plus|in c\+\+|using c\+\+|with c\+\+|c\+\+ program|c\+\+ code|c\+\+ implementation|c\+\+ solution|c\+\+ algorithm|c\+\+ class|c\+\+ function)\b'
#         is_cpp_request = bool(re.search(cpp_indicators, text, re.IGNORECASE))
        
#         cpp_solution_request = bool(re.search(r'\b(solution|code|program|implementation|algorithm).{1,20}(in|using|with) c\+\+\b', text, re.IGNORECASE))
#         if cpp_solution_request:
#             is_cpp_request = True
        
#         programming_patterns = [
#             r'given an (array|input|integer|string|vector|list|graph|tree)',
#             r'write a (function|program|method|algorithm)',
#             r'implement a (function|program|method|algorithm)',
#             r'create a (function|program|method|algorithm)',
#             r'find the (maximum|minimum|average|sum|product|median)',
#             r'time complexity.*space complexity',
#             r'return the (result|output|answer|value)',
#             r'O\(n\)|O\(n²\)|O\(n log n\)|O\(1\)',
#         ]
#         has_programming_pattern = any(bool(re.search(pattern, text, re.IGNORECASE)) for pattern in programming_patterns)
        
#         io_example_pattern = r'(input|example|test case).*?:\s*.*?\s*(output|result).*?:'
#         has_io_example = bool(re.search(io_example_pattern, text, re.IGNORECASE | re.DOTALL))
        
#         is_coding_problem = has_programming_pattern or has_io_example or is_code_task
        
#         if is_coding_problem and not is_cpp_request:
#             other_languages = r'\b(python|java|javascript|typescript|golang|ruby|rust|swift|php|c#)\b'
#             if not bool(re.search(other_languages, text, re.IGNORECASE)):
#                 is_cpp_request = True
#                 logging.info("Coding problem detected with no specific language, defaulting to C++")
        
#         meaningful_text_question = has_question_mark and len(text) > 20
        
#         is_meaningful = (has_question_words and (len(text) > 20)) or \
#                        has_code_keywords or \
#                        is_code_task or \
#                        is_cpp_request or \
#                        is_coding_problem or \
#                        has_programming_pattern or \
#                        has_io_example or \
#                        meaningful_text_question
                       
#         logging.info(f"Question analysis: has_question_mark={has_question_mark}, has_question_words={has_question_words}, "
#                      f"has_code_keywords={has_code_keywords}, is_code_task={is_code_task}, is_cpp_request={is_cpp_request}, "
#                      f"is_coding_problem={is_coding_problem}, has_programming_pattern={has_programming_pattern}, "
#                      f"decision={is_meaningful}")
        
#         return is_meaningful, is_cpp_request

#     def format_response(self, response, is_code_response=False):
#         """
#         Improved formatting of the Gemini response for better readability,
#         with special handling for C++ code.
#         """
#         if not response:
#             return "No response received from AI model."
        
#         if "```" in response or "###" in response:
#             if is_code_response and "```cpp" not in response and "```c++" not in response:
#                 response = response.replace("```", "```cpp", 1)
#             return response
            
#         code_block_start = re.search(r'(Here\'s|This is|The|A) (the )?(complete |full )?(code|solution|implementation|program)', response, re.IGNORECASE)
        
#         if is_code_response or code_block_start:
#             code_lines = []
#             explanation_lines = []
#             in_code_block = False
            
#             lines = response.split('\n')
#             for i, line in enumerate(lines):
#                 if not in_code_block and (
#                     code_block_start and i >= code_block_start.start() or
#                     line.strip().startswith('#include') or 
#                     line.strip().startswith('using namespace') or
#                     line.strip().startswith('int main') or
#                     line.strip().startswith('class ') or
#                     line.strip().startswith('struct ') or
#                     line.strip().startswith('template<') or
#                     line.strip().startswith('void ') or
#                     line.strip().startswith('int ') or
#                     line.strip().startswith('bool ') or
#                     line.strip().startswith('string ') or
#                     line.strip().startswith('vector<') or
#                     line.strip().startswith('def ') or
#                     line.strip().startswith('public class') or
#                     line.strip().startswith('// ') or
#                     line.strip().startswith('/*')
#                 ):
#                     explanation_lines.extend(lines[:i])
#                     in_code_block = True
#                     code_lines.append(line)
#                 elif in_code_block:
#                     code_lines.append(line)
            
#             if code_lines:
#                 explanation_text = '\n'.join(explanation_lines).strip()
#                 code_text = '\n'.join(code_lines).strip()
                
#                 lang = "cpp" if (
#                     is_code_response or
#                     any(cpp_keyword in code_text for cpp_keyword in [
#                         '#include', 'using namespace std', 'int main', 'cout', 'cin', 
#                         'vector<', 'std::', '::iterator', '->', 'nullptr', 'template<',
#                         'auto ', 'const ', 'void ', 'bool ', 'static_cast<'
#                     ])
#                 ) else "python"
                
#                 formatted_response = explanation_text + "\n\n```" + lang + "\n" + code_text + "\n```"
#                 return formatted_response.strip()
        
#         paragraphs = re.split(r'\n\s*\n', response)
#         formatted_paragraphs = []
        
#         for para in paragraphs:
#             if re.match(r'^[A-Z][A-Za-z\s]+:$', para.strip()) or para.strip().isupper():
#                 formatted_paragraphs.append(f"### {para.strip()}")
#             else:
#                 formatted_paragraphs.append(para.strip())
                
#         return "\n\n".join(formatted_paragraphs)

#     def clean_response(self, response):
#         """Remove unnecessary parts of the response to make it more concise."""
#         cleaned = re.sub(r"I'm an AI (assistant|model).*?knowledge cutoff.*?\.", "", response, flags=re.DOTALL|re.IGNORECASE)
#         cleaned = re.sub(r"As an AI (assistant|model).*?knowledge cutoff.*?\.", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
#         cleaned = re.sub(r"(I'd be happy to|I'd be glad to|I can certainly|Let me|Here's|I'll|I will) (help|assist|provide|create|write|solve|answer).*?\.", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
#         cleaned = re.sub(r"(I hope this helps|Let me know if you need any clarification|If you have any questions).*$", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
#         cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
#         return cleaned.strip()

#     def send_to_api(self, response):
#         """Send the Gemini response to the specified API endpoint."""
#         try:
#             payload = {
#                 "message": response,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
#             headers = {
#                 "Content-Type": "application/json",
#                 "x-api-key": API_KEY
#             }
#             api_response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
#             api_response.raise_for_status()
#             logging.info(f"Successfully sent response to API: {api_response.status_code}")
#             return api_response.json() if api_response.content else {"status": "success"}
#         except requests.exceptions.HTTPError as e:
#             logging.error(f"HTTP error sending response to API: {e}, Status: {e.response.status_code}")
#             try:
#                 error_details = e.response.json()
#             except ValueError:
#                 error_details = e.response.text
#             return {"error": str(e), "status_code": e.response.status_code, "details": error_details}
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Error sending response to API: {e}")
#             return {"error": str(e)}

#     def get_gemini_response(self, text, is_cpp_request=False):
#         """
#         Improved prompt engineering for getting better C++ responses from Gemini.
#         """
#         try:
#             available_models = get_available_models()
            
#             if not available_models:
#                 logging.error("No Gemini models available. Check API key and quotas.")
#                 return "No Gemini models are available. Please check your API key and quotas."
            
#             errors = []
#             for model_name in available_models[:3]:
#                 try:
#                     logging.info(f"Attempting to use model: {model_name}")
#                     model = genai.GenerativeModel(model_name)
                    
#                     if is_cpp_request:
#                         prompt = (
#                             f"The following text appears to contain a C++ coding problem or request:\n\n{text}\n\n"
#                             f"You MUST provide a complete and professional C++ solution with the following structure:\n"
#                             f"1. A brief explanation of the approach and algorithm\n"
#                             f"2. The full, well-commented C++ code that solves the problem\n"
#                             f"3. Include all necessary headers (e.g., iostream, vector, string, etc.)\n"
#                             f"4. Use proper namespace declarations (using namespace std;)\n"
#                             f"5. Make sure the main() function is complete and demonstrates usage\n"
#                             f"6. Include test cases or example inputs/outputs where appropriate\n"
#                             f"7. Ensure the code is complete, efficient, and follows C++ best practices\n"
#                             f"8. Use modern C++ features when appropriate (C++11/14/17 features)\n"
#                             f"The code must be directly compilable without any modifications.\n"
#                             f"Do not include apologies, disclaimers or statements about your capabilities."
#                         )
#                     else:
#                         prompt = (
#                             f"The following text appears to contain a question or a programming problem:\n\n{text}\n\n"
#                             f"Provide a complete and detailed solution to the question or problem. "
#                             f"If it's a coding problem, include the full code with explanations. "
#                             f"If it's a textual question, provide a comprehensive answer with clear reasoning. "
#                             f"Be concise and avoid unnecessary apologies or disclaimers."
#                         )
                    
#                     max_retries = 2
#                     backoff_time = RATE_LIMIT_BACKOFF
                    
#                     for attempt in range(max_retries):
#                         try:
#                             response = model.generate_content(prompt)
#                             logging.info(f"Successfully used model {model_name}")
#                             raw_response = response.text.strip()
                            
#                             cleaned_response = self.clean_response(raw_response)
#                             formatted_response = self.format_response(cleaned_response, is_cpp_request)
                            
#                             if is_cpp_request and "```cpp" not in formatted_response and "#include" not in formatted_response:
#                                 logging.warning("C++ solution requested but not detected. Retrying with explicit prompt.")
#                                 cpp_rescue_prompt = (
#                                     f"IMPORTANT: You MUST provide a C++ solution for this problem:\n\n{text}\n\n"
#                                     f"Write ONLY C++ code that includes:\n"
#                                     f"1. All necessary headers (#include statements)\n"
#                                     f"2. Namespace declaration (using namespace std;)\n"
#                                     f"3. A complete main() function\n"
#                                     f"4. Full implementation of all required functions/classes\n"
#                                     f"The solution must be in C++ ONLY, not any other language. Your response should start with #include statements."
#                                 )
#                                 retry_response = model.generate_content(cpp_rescue_prompt)
#                                 retry_raw = retry_response.text.strip()
#                                 retry_cleaned = self.clean_response(retry_raw)
#                                 retry_formatted = self.format_response(retry_cleaned, True)
                                
#                                 if "```cpp" in retry_formatted or "#include" in retry_formatted:
#                                     logging.info("Successfully retrieved C++ solution on retry")
#                                     return retry_formatted
#                                 else:
#                                     logging.warning("Failed to get C++ code even with explicit retry")
                            
#                             return formatted_response
#                         except Exception as retry_error:
#                             if "429" in str(retry_error) and attempt < max_retries - 1:
#                                 logging.warning(f"Rate limited. Waiting {backoff_time} seconds before retry...")
#                                 time.sleep(backoff_time)
#                                 backoff_time *= 2
#                             else:
#                                 raise
#                 except Exception as model_error:
#                     errors.append(f"{model_name}: {str(model_error)}")
#                     logging.warning(f"Model {model_name} failed: {str(model_error)}")
#                     continue
            
#             error_msg = "All Gemini models failed. Errors:\n" + "\n".join(errors)
#             logging.error(error_msg)
#             return "Failed to get response from any AI model. You may have exceeded your quota limits or the models may be unavailable."
            
#         except Exception as e:
#             logging.error(f"Error getting Gemini response: {e}")
#             return f"Gemini API Error: {str(e)}. You may have exceeded your quota limits."

#     def detect_coding_problem_type(self, text):
#         """
#         Advanced detection to determine if a text likely contains a coding problem
#         and what language is preferred or required.
#         """
#         cpp_indicators = r'\b(c\+\+|cpp|c plus plus|in c\+\+|using c\+\+|with c\+\+)\b'
#         is_cpp_explicit = bool(re.search(cpp_indicators, text, re.IGNORECASE))
        
#         cpp_implicit = any(keyword in text for keyword in [
#             'iostream', '#include', 'cin>>', 'cout<<', 'namespace std', 'vector<', 
#             'std::', '::iterator', 'nullptr', 'template<', 'constexpr'
#         ])
        
#         python_indicators = r'\b(python|\.py|def |import |from \w+ import)\b'
#         java_indicators = r'\b(java|public class|public static void main)\b'
#         js_indicators = r'\b(javascript|js|node\.js|const |let |function\s+\w+\(\))\b'
        
#         is_python = bool(re.search(python_indicators, text, re.IGNORECASE))
#         is_java = bool(re.search(java_indicators, text, re.IGNORECASE))
#         is_javascript = bool(re.search(js_indicators, text, re.IGNORECASE))
        
#         code_problem_indicators = [
#             r'implement (a|an|the) (function|algorithm|solution)',
#             r'write (a|an|the) (function|algorithm|program)',
#             r'time complexity',
#             r'given an (array|string|integer|vector|list|input)',
#             r'find the (maximum|minimum|sum|average|median)',
#             r'return the (result|answer|output)',
#             r'example input.*example output',
#             r'test case',
#             r'problem statement',
#             r'leetcode|hackerrank|codeforces'
#         ]
        
#         is_coding_problem = any(bool(re.search(pattern, text, re.IGNORECASE)) for pattern in code_problem_indicators)
        
#         if is_cpp_explicit or cpp_implicit:
#             return is_coding_problem, True
#         elif is_python or is_java or is_javascript:
#             return is_coding_problem, False
#         elif is_coding_problem:
#             return True, True
#         else:
#             return False, False

#     def process_screenshot(self):
#         path = self.take_screenshot()
#         if not path:
#             return

#         text = self.extract_text(path)
#         if not text:
#             logging.warning("No text found in screenshot.")
#             return

#         is_coding_problem, is_cpp_default = self.detect_coding_problem_type(text)
#         is_meaningful, is_cpp_explicit = self.is_meaningful_question(text)
        
#         is_cpp_request = is_cpp_explicit or (is_coding_problem and is_cpp_default)
        
#         if not is_meaningful and not is_coding_problem:
#             logging.info("No meaningful question or coding problem detected in screenshot. Skipping.")
#             return
            
#         if is_coding_problem:
#             logging.info(f"Coding problem detected. Is C++ requested: {is_cpp_request}")
#         else:
#             logging.info(f"Meaningful question detected. Is C++ requested: {is_cpp_request}")
            
#         response = self.get_gemini_response(text, is_cpp_request)
#         api_result = self.send_to_api(response)
        
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         logging.info(f"\n=== SCREENSHOT ANALYSIS ({timestamp}) ===\n")
        
#         if is_cpp_request:
#             logging.info(f"Detected: Coding problem requiring C++ solution")
#         elif is_coding_problem:
#             logging.info(f"Detected: Coding problem (general)")
#         else:
#             logging.info(f"Detected: Meaningful question")
            
#         logging.info(f"\nGemini Response:\n{response}\n")
#         logging.info(f"API Response:\n{api_result}\n")
#         # for screenshot--------------------api
# @app.route('/take-screenshot', methods=['POST'])
# def trigger_screenshot():
#     """API endpoint to trigger screenshot on demand"""
#     logging.info("=== SCREENSHOT API ENDPOINT CALLED ===")
#     try:
#         # Verify API key if needed
#         api_key = request.headers.get('x-api-key')
#         if api_key != API_KEY:
#             return jsonify({"error": "Invalid API key"}), 401
        
#         # Create monitor instance and process screenshot
#         monitor = ScreenshotMonitor(interval=INTERVAL, screenshots_dir=SCREENSHOTS_DIR)
#         monitor.process_screenshot()
        
#         return jsonify({"status": "Screenshot processed successfully"}), 200
#     except Exception as e:
#         logging.error(f"Error processing screenshot request: {e}")
#         return jsonify({"error": str(e)}), 500
# def test_gemini_connection():
#     try:
#         logging.info("Testing Gemini API connection...")
#         available_models = get_available_models()
        
#         if not available_models:
#             logging.error("No models available for content generation. Check your API key and permissions.")
#             return False
        
#         model_name = available_models[0]
#         logging.info(f"Testing with available model: {model_name}")
#         model = genai.GenerativeModel(model_name)
#         response = model.generate_content("Test")
#         logging.info(f"Gemini API connection successful with model {model_name}!")
#         return True
#     except Exception as e:
#         logging.error(f"Gemini API connection failed: {e}")
#         if "429" in str(e):
#             logging.error("Hit rate limits with your API key. Consider waiting, using a different key, or upgrading quota.")
#         elif "404" in str(e) and len(available_models) > 1:
#             logging.info(f"Trying alternative model: {available_models[1]}")
#             try:
#                 model = genai.GenerativeModel(available_models[1])
#                 response = model.generate_content("Test")
#                 logging.info(f"Gemini API connection successful with model {available_models[1]}!")
#                 return True
#             except Exception as e2:
#                 logging.error(f"Alternative model also failed: {e2}")
#         return False

# # Set your ngrok authtoken
# ngrok.set_auth_token("2xmjcFxnZbEg8uzm0D8X8vKiauU_3xTUtqi7DPRP9wvUYBWKw")

# import threading
# from pyngrok import ngrok

# # Set your ngrok authtoken
# ngrok.set_auth_token("2xmjcFxnZbEg8uzm0D8X8vKiauU_3xTUtqi7DPRP9wvUYBWKw")

# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 5000))
    
#     try:
#         if not test_gemini_connection():
#             logging.error("Gemini API connection failed. Exiting.")
#             sys.exit(1)
        
#         if not test_api_endpoint():
#             logging.error("API endpoint test failed. Exiting.")
#             sys.exit(1)
        
#         print("=== STARTING FLASK SERVER WITH NGROK ===")
#         logging.info("Starting Flask server with ngrok tunnel")
        
#         # Start ngrok tunnel
#         public_url = ngrok.connect(port)
#         print(f"🌐 ngrok tunnel URL: {public_url}")
#         logging.info(f"ngrok tunnel created: {public_url}")
        
#         # Run Flask app directly in main thread (no threading needed)
#         try:
#             app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
#         except KeyboardInterrupt:
#             print("\n🛑 Shutting down...")
#             ngrok.disconnect(public_url)
#             ngrok.kill()
            
#     except Exception as e:
#         logging.error(f"Fatal error: {e}")
#         print(f"❌ Fatal error: {e}")
#         # Clean up ngrok on error
#         try:
#             ngrok.kill()
#         except:
#             pass
#         # new code-------------------------------------------------
# import os
# import time
# import logging
# import sys
# import re
# from datetime import datetime
# from PIL import ImageGrab, Image
# import pytesseract
# import google.generativeai as genai
# import requests
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import tempfile
# import io

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# # Configuration
# GEMINI_API_KEY = "AIzaSyCe_GBJsN9z9wCruEyKezHIPPZEkbGfv5Y"
# API_ENDPOINT = "https://message-web-4.onrender.com/messages"
# API_KEY = "X7kP9mW3qT2rY8nF4vJ6hL5zB1cD"
# SCREENSHOTS_DIR = "screenshots"

# # Setup logging
# log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot_monitor.log")
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
# )

# # Configure Gemini
# genai.configure(api_key=GEMINI_API_KEY)

# # Test API endpoint
# def test_api_endpoint():
#     try:
#         logging.info("Testing API endpoint...")
#         payload = {"message": "Test message", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#         headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
#         response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
#         response.raise_for_status()
#         logging.info(f"API endpoint test successful: {response.status_code}")
#         return True
#     except requests.exceptions.RequestException as e:
#         logging.error(f"API endpoint test failed: {e}")
#         return False

# def test_gemini_connection():
#     try:
#         logging.info("Testing Gemini API connection...")
#         model = genai.GenerativeModel('gemini-pro')
#         response = model.generate_content("Test connection")
#         logging.info("Gemini API connection successful!")
#         return True
#     except Exception as e:
#         logging.error(f"Gemini API connection failed: {e}")
#         return False

# class ImageProcessor:
#     def __init__(self):
#         # Set Tesseract path (adjust for your environment)
#         pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
#     def extract_text(self, image_data):
#         """Extract text from image bytes"""
#         try:
#             img = Image.open(io.BytesIO(image_data))
#             text = pytesseract.image_to_string(img)
#             return text.strip()
#         except Exception as e:
#             logging.error(f"Error extracting text: {e}")
#             return ""

#     def is_meaningful_question(self, text):
#         """Detect if text contains a meaningful question or coding problem"""
#         # Same implementation as before
#         # ... (keep your existing implementation here) ...
#         return True, True  # Simplified for example

#     def get_gemini_response(self, text, is_cpp_request=False):
#         """Get response from Gemini API"""
#         # Same implementation as before
#         # ... (keep your existing implementation here) ...
#         return "Gemini response"  # Simplified for example

#     def format_response(self, response, is_code_response=False):
#         """Format Gemini response"""
#         # Same implementation as before
#         # ... (keep your existing implementation here) ...
#         return response

#     def clean_response(self, response):
#         """Clean Gemini response"""
#         # Same implementation as before
#         # ... (keep your existing implementation here) ...
#         return response

#     def send_to_api(self, response):
#         """Send response to message website"""
#         try:
#             payload = {
#                 "message": response,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
#             headers = {
#                 "Content-Type": "application/json",
#                 "x-api-key": API_KEY
#             }
#             api_response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
#             api_response.raise_for_status()
#             logging.info(f"Successfully sent response to API: {api_response.status_code}")
#             return True
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Error sending response to API: {e}")
#             return False

# # Create processor instance
# processor = ImageProcessor()

# # API Endpoints
# @app.route('/test', methods=['GET'])
# def test_endpoint():
#     return jsonify({"status": "API is running"}), 200

# @app.route('/take-screenshot', methods=['POST'])
# def handle_take_screenshot():
#     """Endpoint to process screenshot command"""
#     try:
#         # Take screenshot
#         logging.info("Taking screenshot...")
#         image = ImageGrab.grab()
        
#         # Convert to bytes
#         img_byte_arr = io.BytesIO()
#         image.save(img_byte_arr, format='PNG')
#         img_byte_arr = img_byte_arr.getvalue()
        
#         # Extract text
#         text = processor.extract_text(img_byte_arr)
        
#         # Send to message website
#         success = processor.send_to_api(f"Extracted text: {text}")
        
#         return jsonify({
#             "status": "success",
#             "action": "take-screenshot",
#             "text_extracted": text[:100] + "..." if text else "",
#             "api_response": "Sent to message website" if success else "Failed to send"
#         }), 200
        
#     except Exception as e:
#         logging.error(f"Error processing take-screenshot: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/send-solution', methods=['POST'])
# def handle_send_solution():
#     """Endpoint to process send-solution command"""
#     try:
#         # Get image data from request
#         if 'image' not in request.files:
#             return jsonify({"error": "No image provided"}), 400
            
#         image_file = request.files['image']
#         image_data = image_file.read()
        
#         # Extract text
#         text = processor.extract_text(image_data)
#         if not text:
#             return jsonify({"error": "No text extracted from image"}), 400
        
#         # Get Gemini response
#         _, is_cpp = processor.is_meaningful_question(text)
#         gemini_response = processor.get_gemini_response(text, is_cpp)
        
#         # Format and send response
#         formatted_response = processor.format_response(gemini_response, is_cpp)
#         success = processor.send_to_api(formatted_response)
        
#         return jsonify({
#             "status": "success",
#             "action": "send-solution",
#             "gemini_response": formatted_response[:500] + "..." if formatted_response else "",
#             "api_response": "Sent to message website" if success else "Failed to send"
#         }), 200
        
#     except Exception as e:
#         logging.error(f"Error processing send-solution: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/send-extracted-text', methods=['POST'])
# def handle_send_extracted_text():
#     """Endpoint to process send-extracted-text command"""
#     try:
#         # Get image data from request
#         if 'image' not in request.files:
#             return jsonify({"error": "No image provided"}), 400
            
#         image_file = request.files['image']
#         image_data = image_file.read()
        
#         # Extract text
#         text = processor.extract_text(image_data)
#         if not text:
#             return jsonify({"error": "No text extracted from image"}), 400
        
#         # Send to message website
#         success = processor.send_to_api(text)
        
#         return jsonify({
#             "status": "success",
#             "action": "send-extracted-text",
#             "text_extracted": text[:500] + "..." if text else "",
#             "api_response": "Sent to message website" if success else "Failed to send"
#         }), 200
        
#     except Exception as e:
#         logging.error(f"Error processing send-extracted-text: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/process-command', methods=['POST'])
# def process_command():
#     """Unified endpoint for all commands"""
#     try:
#         # Verify API key
#         api_key = request.headers.get('x-api-key')
#         if api_key != API_KEY:
#             return jsonify({"error": "Invalid API key"}), 401
        
#         # Get command from request
#         command = request.json.get('command')
#         if not command:
#             return jsonify({"error": "No command provided"}), 400
        
#         # Process based on command type
#         if command == 'take-screenshot':
#             # Take screenshot
#             image = ImageGrab.grab()
#             img_byte_arr = io.BytesIO()
#             image.save(img_byte_arr, format='PNG')
#             img_data = img_byte_arr.getvalue()
            
#             # Extract text
#             text = processor.extract_text(img_data)
#             processor.send_to_api(f"Extracted text: {text}")
            
#             return jsonify({
#                 "status": "success",
#                 "command": command,
#                 "result": "Screenshot taken and text extracted"
#             })
            
#         elif command == 'send-solution':
#             # Get image data
#             image_data = request.json.get('image_data')
#             if not image_data:
#                 return jsonify({"error": "No image data provided"}), 400
                
#             # Extract text and get solution
#             text = processor.extract_text(image_data)
#             _, is_cpp = processor.is_meaningful_question(text)
#             response = processor.get_gemini_response(text, is_cpp)
#             formatted = processor.format_response(response, is_cpp)
#             processor.send_to_api(formatted)
            
#             return jsonify({
#                 "status": "success",
#                 "command": command,
#                 "result": "Solution generated and sent"
#             })
            
#         elif command == 'send-extracted-text':
#             # Get image data
#             image_data = request.json.get('image_data')
#             if not image_data:
#                 return jsonify({"error": "No image data provided"}), 400
                
#             # Extract and send text
#             text = processor.extract_text(image_data)
#             processor.send_to_api(text)
            
#             return jsonify({
#                 "status": "success",
#                 "command": command,
#                 "result": "Extracted text sent"
#             })
            
#         else:
#             return jsonify({"error": "Invalid command"}), 400
            
#     except Exception as e:
#         logging.error(f"Error processing command: {e}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     # Verify services
#     if not test_gemini_connection():
#         logging.error("Gemini API connection failed. Exiting.")
#         sys.exit(1)
        
#     if not test_api_endpoint():
#         logging.error("Message API connection failed. Exiting.")
#         sys.exit(1)
    
#     # Get port from environment variable or use default
#     port = int(os.environ.get('PORT', 5000))
    
#     # Start Flask app
#     logging.info(f"Starting API server on port {port}")
#     app.run(host='0.0.0.0', port=port)
# code 6--------------------------------------------------------------
import os
import time
import logging
import re
from datetime import datetime
import pytesseract
import google.generativeai as genai
import requests
from flask import Flask, request, jsonify
from PIL import Image
import sys 
from flask_cors import CORS
import io
import base64

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
GEMINI_API_KEY = "AIzaSyCe_GBJsN9z9wCruEyKezHIPPZEkbGfv5Y"
API_ENDPOINT = "https://message-web-4.onrender.com/messages"
API_KEY = "X7kP9mW3qT2rY8nF4vJ6hL5zB1cD"
SCREENSHOTS_DIR = "screenshots"

# Setup logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshot_monitor.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Test API endpoint
def test_api_endpoint():
    try:
        logging.info("Testing API endpoint...")
        payload = {"message": "Test message", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"API endpoint test successful: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"API endpoint test failed: {e}")
        return False

def test_gemini_connection():
    try:
        logging.info("Testing Gemini API connection...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Test connection")
        logging.info("Gemini API connection successful!")
        return True
    except Exception as e:
        logging.error(f"Gemini API connection failed: {e}")
        return False

class ImageProcessor:
    def __init__(self):
        # Set Tesseract path (adjust for your environment)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def extract_text(self, image_data):
        """Extract text from image bytes"""
        try:
            img = Image.open(io.BytesIO(image_data))
            return pytesseract.image_to_string(img).strip()
        except Exception as e:
            logging.error(f"Error extracting text: {e}")
            return ""

    def is_meaningful_question(self, text):
        """
        Enhanced detection of meaningful questions with better code problem detection,
        especially focusing on C++ requests.
        """
        question_indicators = r'\b(what|why|how|when|where|who|which|can|could|should|would|is|are|does|do|solve|find|calculate|explain|write|create|implement|develop|design)\b'
        has_question_mark = '?' in text
        has_question_words = bool(re.search(question_indicators, text, re.IGNORECASE))
        
        code_indicators = r'\b(code|program|function|class|algorithm|implementation|c\+\+|cpp|python|java|javascript|algorithm|solution|problem|challenge|leetcode|coding|codeforces|hackerrank|programming|assignment|project|task|exercise|homework|development|software|application|implement|develop|write a|create a)\b'
        has_code_keywords = bool(re.search(code_indicators, text, re.IGNORECASE))
        
        code_tasks = r'\b(write|create|develop|implement|design|build|code|program|solve|fix|debug|optimize)\b.{1,70}\b(function|class|method|program|algorithm|solution|problem|code|program|application|system)\b'
        is_code_task = bool(re.search(code_tasks, text, re.IGNORECASE))
        
        cpp_indicators = r'\b(c\+\+|cpp|c plus plus|in c\+\+|using c\+\+|with c\+\+|c\+\+ program|c\+\+ code|c\+\+ implementation|c\+\+ solution|c\+\+ algorithm|c\+\+ class|c\+\+ function)\b'
        is_cpp_request = bool(re.search(cpp_indicators, text, re.IGNORECASE))
        
        cpp_solution_request = bool(re.search(r'\b(solution|code|program|implementation|algorithm).{1,20}(in|using|with) c\+\+\b', text, re.IGNORECASE))
        if cpp_solution_request:
            is_cpp_request = True
        
        programming_patterns = [
            r'given an (array|input|integer|string|vector|list|graph|tree)',
            r'write a (function|program|method|algorithm)',
            r'implement a (function|program|method|algorithm)',
            r'create a (function|program|method|algorithm)',
            r'find the (maximum|minimum|average|sum|product|median)',
            r'time complexity.*space complexity',
            r'return the (result|output|answer|value)',
            r'O\(n\)|O\(n²\)|O\(n log n\)|O\(1\)',
        ]
        has_programming_pattern = any(bool(re.search(pattern, text, re.IGNORECASE)) for pattern in programming_patterns)
        
        io_example_pattern = r'(input|example|test case).*?:\s*.*?\s*(output|result).*?:'
        has_io_example = bool(re.search(io_example_pattern, text, re.IGNORECASE | re.DOTALL))
        
        is_coding_problem = has_programming_pattern or has_io_example or is_code_task
        
        if is_coding_problem and not is_cpp_request:
            other_languages = r'\b(python|java|javascript|typescript|golang|ruby|rust|swift|php|c#)\b'
            if not bool(re.search(other_languages, text, re.IGNORECASE)):
                is_cpp_request = True
                logging.info("Coding problem detected with no specific language, defaulting to C++")
        
        meaningful_text_question = has_question_mark and len(text) > 20
        
        is_meaningful = (has_question_words and (len(text) > 20)) or \
                       has_code_keywords or \
                       is_code_task or \
                       is_cpp_request or \
                       is_coding_problem or \
                       has_programming_pattern or \
                       has_io_example or \
                       meaningful_text_question
                       
        logging.info(f"Question analysis: has_question_mark={has_question_mark}, has_question_words={has_question_words}, "
                     f"has_code_keywords={has_code_keywords}, is_code_task={is_code_task}, is_cpp_request={is_cpp_request}, "
                     f"is_coding_problem={is_coding_problem}, has_programming_pattern={has_programming_pattern}, "
                     f"decision={is_meaningful}")
        
        return is_meaningful, is_cpp_request

    def get_gemini_response(self, text, is_cpp_request=False):
        """
        Improved prompt engineering for getting better C++ responses from Gemini.
        """
        try:
            available_models = [
                "models/gemini-1.5-flash",
                "models/gemini-1.5-flash-latest",
                "models/gemini-2.0-flash-lite",
                "models/gemini-2.5-flash-preview",
                "models/gemini-1.5-flash",
#             "models/gemini-1.5-flash-latest",
#             "models/gemini-2.0-flash-lite",
#             "models/gemini-2.5-flash-preview"
            ]
            
            errors = []
            for model_name in available_models[:3]:
                try:
                    logging.info(f"Attempting to use model: {model_name}")
                    model = genai.GenerativeModel(model_name)
                    
                    if is_cpp_request:
                        prompt = (
                            f"The following text appears to contain a C++ coding problem or request:\n\n{text}\n\n"
                            f"You MUST provide a complete and professional C++ solution with the following structure:\n"
                            f"1. A brief explanation of the approach and algorithm\n"
                            f"2. The full, well-commented C++ code that solves the problem\n"
                            f"3. Include all necessary headers (e.g., iostream, vector, string, etc.)\n"
                            f"4. Use proper namespace declarations (using namespace std;)\n"
                            f"5. Make sure the main() function is complete and demonstrates usage\n"
                            f"6. Include test cases or example inputs/outputs where appropriate\n"
                            f"7. Ensure the code is complete, efficient, and follows C++ best practices\n"
                            f"8. Use modern C++ features when appropriate (C++11/14/17 features)\n"
                            f"The code must be directly compilable without any modifications.\n"
                            f"Do not include apologies, disclaimers or statements about your capabilities."
                        )
                    else:
                        prompt = (
                            f"The following text appears to contain a question or a programming problem:\n\n{text}\n\n"
                            f"Provide a complete and detailed solution to the question or problem. "
                            f"If it's a coding problem, include the full code with explanations. "
                            f"If it's a textual question, provide a comprehensive answer with clear reasoning. "
                            f"Be concise and avoid unnecessary apologies or disclaimers."
                        )
                    
                    max_retries = 2
                    backoff_time = 60  # seconds
                    
                    for attempt in range(max_retries):
                        try:
                            response = model.generate_content(prompt)
                            logging.info(f"Successfully used model {model_name}")
                            raw_response = response.text.strip()
                            
                            cleaned_response = self.clean_response(raw_response)
                            formatted_response = self.format_response(cleaned_response, is_cpp_request)
                            
                            if is_cpp_request and "```cpp" not in formatted_response and "#include" not in formatted_response:
                                logging.warning("C++ solution requested but not detected. Retrying with explicit prompt.")
                                cpp_rescue_prompt = (
                                    f"IMPORTANT: You MUST provide a C++ solution for this problem:\n\n{text}\n\n"
                                    f"Write ONLY C++ code that includes:\n"
                                    f"1. All necessary headers (#include statements)\n"
                                    f"2. Namespace declaration (using namespace std;)\n"
                                    f"3. A complete main() function\n"
                                    f"4. Full implementation of all required functions/classes\n"
                                    f"The solution must be in C++ ONLY, not any other language. Your response should start with #include statements."
                                )
                                retry_response = model.generate_content(cpp_rescue_prompt)
                                retry_raw = retry_response.text.strip()
                                retry_cleaned = self.clean_response(retry_raw)
                                retry_formatted = self.format_response(retry_cleaned, True)
                                
                                if "```cpp" in retry_formatted or "#include" in retry_formatted:
                                    logging.info("Successfully retrieved C++ solution on retry")
                                    return retry_formatted
                                else:
                                    logging.warning("Failed to get C++ code even with explicit retry")
                            
                            return formatted_response
                        except Exception as retry_error:
                            if "429" in str(retry_error) and attempt < max_retries - 1:
                                logging.warning(f"Rate limited. Waiting {backoff_time} seconds before retry...")
                                time.sleep(backoff_time)
                                backoff_time *= 2
                            else:
                                raise
                except Exception as model_error:
                    errors.append(f"{model_name}: {str(model_error)}")
                    logging.warning(f"Model {model_name} failed: {str(model_error)}")
                    continue
            
            error_msg = "All Gemini models failed. Errors:\n" + "\n".join(errors)
            logging.error(error_msg)
            return "Failed to get response from any AI model. You may have exceeded your quota limits or the models may be unavailable."
            
        except Exception as e:
            logging.error(f"Error getting Gemini response: {e}")
            return f"Gemini API Error: {str(e)}. You may have exceeded your quota limits."

    def format_response(self, response, is_code_response=False):
        """
        Improved formatting of the Gemini response for better readability,
        with special handling for C++ code.
        """
        if not response:
            return "No response received from AI model."
        
        if "```" in response or "###" in response:
            if is_code_response and "```cpp" not in response and "```c++" not in response:
                response = response.replace("```", "```cpp", 1)
            return response
            
        code_block_start = re.search(r'(Here\'s|This is|The|A) (the )?(complete |full )?(code|solution|implementation|program)', response, re.IGNORECASE)
        
        if is_code_response or code_block_start:
            code_lines = []
            explanation_lines = []
            in_code_block = False
            
            lines = response.split('\n')
            for i, line in enumerate(lines):
                if not in_code_block and (
                    code_block_start and i >= code_block_start.start() or
                    line.strip().startswith('#include') or 
                    line.strip().startswith('using namespace') or
                    line.strip().startswith('int main') or
                    line.strip().startswith('class ') or
                    line.strip().startswith('struct ') or
                    line.strip().startswith('template<') or
                    line.strip().startswith('void ') or
                    line.strip().startswith('int ') or
                    line.strip().startswith('bool ') or
                    line.strip().startswith('string ') or
                    line.strip().startswith('vector<') or
                    line.strip().startswith('def ') or
                    line.strip().startswith('public class') or
                    line.strip().startswith('// ') or
                    line.strip().startswith('/*')
                ):
                    explanation_lines.extend(lines[:i])
                    in_code_block = True
                    code_lines.append(line)
                elif in_code_block:
                    code_lines.append(line)
            
            if code_lines:
                explanation_text = '\n'.join(explanation_lines).strip()
                code_text = '\n'.join(code_lines).strip()
                
                lang = "cpp" if (
                    is_code_response or
                    any(cpp_keyword in code_text for cpp_keyword in [
                        '#include', 'using namespace std', 'int main', 'cout', 'cin', 
                        'vector<', 'std::', '::iterator', '->', 'nullptr', 'template<',
                        'auto ', 'const ', 'void ', 'bool ', 'static_cast<'
                    ])
                ) else "python"
                
                formatted_response = explanation_text + "\n\n```" + lang + "\n" + code_text + "\n```"
                return formatted_response.strip()
        
        paragraphs = re.split(r'\n\s*\n', response)
        formatted_paragraphs = []
        
        for para in paragraphs:
            if re.match(r'^[A-Z][A-Za-z\s]+:$', para.strip()) or para.strip().isupper():
                formatted_paragraphs.append(f"### {para.strip()}")
            else:
                formatted_paragraphs.append(para.strip())
                
        return "\n\n".join(formatted_paragraphs)

    def clean_response(self, response):
        """Remove unnecessary parts of the response to make it more concise."""
        cleaned = re.sub(r"I'm an AI (assistant|model).*?knowledge cutoff.*?\.", "", response, flags=re.DOTALL|re.IGNORECASE)
        cleaned = re.sub(r"As an AI (assistant|model).*?knowledge cutoff.*?\.", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
        cleaned = re.sub(r"(I'd be happy to|I'd be glad to|I can certainly|Let me|Here's|I'll|I will) (help|assist|provide|create|write|solve|answer).*?\.", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
        cleaned = re.sub(r"(I hope this helps|Let me know if you need any clarification|If you have any questions).*$", "", cleaned, flags=re.DOTALL|re.IGNORECASE)
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        return cleaned.strip()

    def send_to_api(self, message):
        """Send the Gemini response to the specified API endpoint."""
        try:
            payload = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "sender": "System"
            }
            headers = {
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            }
            response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            logging.info(f"Message sent to API: {message[:50]}...")
            return True
        except Exception as e:
            logging.error(f"Error sending response to API: {e}")
            return False

# Create processor instance
processor = ImageProcessor()

# API Endpoints
@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"status": "API is running"}), 200

# @app.route('/take-screenshot', methods=['POST'])
# def handle_take_screenshot():
#     """Endpoint to process screenshot command"""
#     try:
#         # Verify API key
#         api_key = request.headers.get('x-api-key')
#         if api_key != API_KEY:
#             return jsonify({"error": "Invalid API key"}), 401
        
#         # Take screenshot
#         logging.info("Taking screenshot...")
#         image = ImageGrab.grab()
        
#         # Convert to bytes
#         img_byte_arr = io.BytesIO()
#         image.save(img_byte_arr, format='PNG')
#         img_data = img_byte_arr.getvalue()
        
#         # Extract text
#         text = processor.extract_text(img_data)
        
#         # Send to message website
#         success = processor.send_to_api(f"Extracted text: {text}")
        
#         return jsonify({
#             "status": "success",
#             "action": "take-screenshot",
#             "text_extracted": text[:500] + "..." if text else "",
#             "api_response": "Sent to message website" if success else "Failed to send"
#         }), 200
        
#     except Exception as e:
#         logging.error(f"Error processing take-screenshot: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/send-solution', methods=['POST'])
# def handle_send_solution():
#     """Endpoint to process send-solution command"""
#     try:
#         # Verify API key
#         api_key = request.headers.get('x-api-key')
#         if api_key != API_KEY:
#             return jsonify({"error": "Invalid API key"}), 401
        
#         # Get image data from request
#         if 'image' not in request.files:
#             return jsonify({"error": "No image provided"}), 400
            
#         image_file = request.files['image']
#         image_data = image_file.read()
        
#         # Extract text
#         text = processor.extract_text(image_data)
#         if not text:
#             return jsonify({"error": "No text extracted from image"}), 400
        
#         # Check if it's a meaningful question and if C++ is requested
#         is_meaningful, is_cpp = processor.is_meaningful_question(text)
#         if not is_meaningful:
#             return jsonify({"error": "No meaningful question detected"}), 400
        
#         # Get Gemini response
#         gemini_response = processor.get_gemini_response(text, is_cpp)
        
#         # Format and send response
#         formatted_response = processor.format_response(gemini_response, is_cpp)
#         success = processor.send_to_api(formatted_response)
        
#         return jsonify({
#             "status": "success",
#             "action": "send-solution",
#             "gemini_response": formatted_response[:500] + "..." if formatted_response else "",
#             "api_response": "Sent to message website" if success else "Failed to send"
#         }), 200
        
#     except Exception as e:
#         logging.error(f"Error processing send-solution: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/send-extracted-text', methods=['POST'])
# def handle_send_extracted_text():
#     """Endpoint to process send-extracted-text command"""
#     try:
#         # Verify API key
#         api_key = request.headers.get('x-api-key')
#         if api_key != API_KEY:
#             return jsonify({"error": "Invalid API key"}), 401
        
#         # Get image data from request
#         if 'image' not in request.files:
#             return jsonify({"error": "No image provided"}), 400
            
#         image_file = request.files['image']
#         image_data = image_file.read()
        
#         # Extract text
#         text = processor.extract_text(image_data)
#         if not text:
#             return jsonify({"error": "No text extracted from image"}), 400
        
#         # Send to message website
#         success = processor.send_to_api(text)
        
#         return jsonify({
#             "status": "success",
#             "action": "send-extracted-text",
#             "text_extracted": text[:500] + "..." if text else "",
#             "api_response": "Sent to message website" if success else "Failed to send"
#         }), 200
        
#     except Exception as e:
#         logging.error(f"Error processing send-extracted-text: {e}")
#         return jsonify({"error": str(e)}), 500

# @app.route('/process-command', methods=['POST'])
# def process_command():
#     """Unified endpoint for all commands"""
#     try:
#         # Verify API key
#         api_key = request.headers.get('x-api-key')
#         if api_key != API_KEY:
#             return jsonify({"error": "Invalid API key"}), 401
        
#         # Get command from request
#         command = request.json.get('command')
#         if not command:
#             return jsonify({"error": "No command provided"}), 400
        
#         # Process based on command type
#         if command == 'take-screenshot':
#             # Take screenshot
#             image = ImageGrab.grab()
#             img_byte_arr = io.BytesIO()
#             image.save(img_byte_arr, format='PNG')
#             img_data = img_byte_arr.getvalue()
            
#             # Extract text
#             text = processor.extract_text(img_data)
#             processor.send_to_api(f"Extracted text: {text}")
            
#             return jsonify({
#                 "status": "success",
#                 "command": command,
#                 "result": "Screenshot taken and text extracted"
#             })
            
#         elif command == 'send-solution':
#             # Get image data
#             image_data = base64.b64decode(request.json.get('image_data'))
#             if not image_data:
#                 return jsonify({"error": "No image data provided"}), 400
                
#             # Extract text and get solution
#             text = processor.extract_text(image_data)
#             _, is_cpp = processor.is_meaningful_question(text)
#             response = processor.get_gemini_response(text, is_cpp)
#             formatted = processor.format_response(response, is_cpp)
#             processor.send_to_api(formatted)
            
#             return jsonify({
#                 "status": "success",
#                 "command": command,
#                 "result": "Solution generated and sent"
#             })
            
#         elif command == 'send-extracted-text':
#             # Get image data
#             image_data = base64.b64decode(request.json.get('image_data'))
#             if not image_data:
#                 return jsonify({"error": "No image data provided"}), 400
                
#             # Extract and send text
#             text = processor.extract_text(image_data)
#             processor.send_to_api(text)
            
#             return jsonify({
#                 "status": "success",
#                 "command": command,
#                 "result": "Extracted text sent"
#             })
            
#         else:
#             return jsonify({"error": "Invalid command"}), 400
            
#     except Exception as e:
#         logging.error(f"Error processing command: {e}")
#         return jsonify({"error": str(e)}), 500
# ADD THIS INSTEAD:

@app.route('/process-action', methods=['POST'])
def handle_action():
    """Unified endpoint for all actions"""
    try:
        # Verify API key
        api_key = request.headers.get('x-api-key')
        if api_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        action = data.get('action')
        if not action:
            return jsonify({"error": "No action specified"}), 400
        
        # Handle different actions
        if action in ['screenshot', 'solution', 'extract-text']:
            # These actions require an image
            if 'image' not in data:
                return jsonify({"error": "No image provided"}), 400
                
            try:
                # Decode base64 image (remove data URL prefix if present)
                image_data = data['image']
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',', 1)[1]
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                logging.error(f"Image decode error: {e}")
                return jsonify({"error": "Invalid image data"}), 400
            
            # Extract text from image
            text = processor.extract_text(image_bytes)
            if not text:
                return jsonify({"error": "No text extracted from image"}), 400
            
            # Action-specific processing
            if action == 'screenshot':
                # For screenshot, just send extracted text
                message = f"📸 Screenshot captured:\n{text}"
                success = processor.send_to_api(message)
                return jsonify({
                    "status": "success",
                    "action": "screenshot",
                    "message": "Screenshot processed"
                })
                
            elif action == 'solution':
                # Check if meaningful question
                is_meaningful, is_cpp = processor.is_meaningful_question(text)
                if not is_meaningful:
                    return jsonify({
                        "status": "success",
                        "action": "solution",
                        "message": "No meaningful question detected"
                    })
                
                # Get Gemini response
                gemini_response = processor.get_gemini_response(text, is_cpp)
                formatted_response = processor.format_response(gemini_response, is_cpp)
                success = processor.send_to_api(formatted_response)
                return jsonify({
                    "status": "success",
                    "action": "solution",
                    "message": "Solution generated and sent"
                })
                
            elif action == 'extract-text':
                # For extract-text, send the extracted text
                success = processor.send_to_api(f"📝 Extracted text:\n{text}")
                return jsonify({
                    "status": "success",
                    "action": "extract-text",
                    "message": "Text extracted and sent"
                })
                
        elif action == 'audio':
            # Audio action (placeholder implementation)
            success = processor.send_to_api("🔊 Audio playback requested")
            return jsonify({
                "status": "success",
                "action": "audio",
                "message": "Audio request processed"
            })
            
        else:
            return jsonify({"error": "Invalid action specified"}), 400
            
    except Exception as e:
        logging.error(f"Error processing action: {e}")
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)