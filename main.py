import requests
import json

API_KEY = "<replace_api_key>"
EXTERNAL_USER_ID = "<replace_external_user_id>"

BASE_URL = "https://api.on-demand.io/chat/v1"

def create_chat_session(api_key, external_user_id):
    url = f"{BASE_URL}/sessions"
    headers = {"apikey": api_key}
    body = {"agentIds": [], "externalUserId": external_user_id}
    try:
        print(f"Attempting to create session at URL: {url}")
        print(f"With headers: {headers}")
        print(f"With body: {json.dumps(body)}")
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 201:
            response_data = response.json()
            session_id = response_data.get("data", {}).get("id")
            if session_id:
                print(f"Chat session created. Session ID: {session_id}")
                return session_id
            else:
                print(
                    f"Error: 'data.id' not found in response. Full response: {response_data}"
                )
                return None
        else:
            print(
                f"Error creating chat session: {response.status_code} - {response.text}"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed during session creation: {e}")
        return None
    except json.JSONDecodeError as e:
        responseText = "N/A"
        if "response" in locals() and hasattr(response, "text"):
            responseText = response.text
        print(
            f"Failed to decode JSON response during session creation: {e}. Response text: {responseText}"
        )
        return None


def submit_query(api_key, session_id, query_text, response_mode="sync"):
    url = f"{BASE_URL}/sessions/{session_id}/query"
    headers = {"apikey": api_key}

    agent_ids_list_str = "[""agent-1712327325", "agent-1713962163", "agent-1713954536", "agent-1713958591", "agent-1713958830", "agent-1713961903", "agent-1713967141"agent_ids_list_str += "]"
    stop_sequences_list_str = "["stop_sequences_list_str += "]"

    body = {
        "endpointId": "predefined-openai-gpt4o-mini",
        "query": query_text,
        "agentIds": json.loads(agent_ids_list_str),
        "responseMode": response_mode,
        "reasoningMode": "medium",
        "modelConfigs": {
            "fulfillmentPrompt": """""",
            "stopSequences": json.loads(stop_sequences_list_str),
            "temperature": 0.7,
            "topP": 1,
            "maxTokens": 0,
            "presencePenalty": 0,
            "frequencyPenalty": 0
        },
    }

    try:
        print(f"Attempting to submit query to URL: {url}")
        print(f"With headers: {headers}")
        print(f"With body: {json.dumps(body, indent=2)}")

        if response_mode == "sync":
            response = requests.post(url, headers=headers, json=body)
            if response.status_code == 200:
                print("Sync query submitted successfully.")
                return response.json()
            else:
                print(
                    f"Error submitting sync query: {response.status_code} - {response.text}"
                )
                return None
        elif response_mode == "stream":
            print(f"Submitting query in stream mode for session {session_id}...")
            response = requests.post(url, headers=headers, json=body, stream=True)
            if response.status_code == 200:
                print("Streaming response:")
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data:"):
                            data_json_str = decoded_line[len("data: ") :].strip()
                            if data_json_str:
                                if data_json_str == "[DONE]":
                                    print("SSE Stream End: [DONE]")
                                    break
                                try:
                                    data_event = json.loads(data_json_str)
                                    print(f"SSE Data: {json.dumps(data_event)}")
                                except json.JSONDecodeError:
                                    print(f"SSE Non-JSON Data: {data_json_str}")
                return "Stream finished"
            else:
                print(
                    f"Error submitting stream query: {response.status_code} - {response.text}"
                )
                return None
        else:
            print(f"Unsupported responseMode: {response_mode}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed during query submission: {e}")
        return None
    except json.JSONDecodeError as e:
        responseText = "N/A"
        if "response" in locals() and hasattr(response, "text"):
            responseText = response.text
        print(
            f"Failed to decode JSON response during sync query: {e}. Response text: {responseText}"
        )
        return None


if __name__ == "__main__":
    if (
        API_KEY == "<replace_api_key>"
        or API_KEY == ""
        or EXTERNAL_USER_ID == "<replace_external_user_id>"
        or EXTERNAL_USER_ID == ""
    ):
        print(
            "Please ensure API_KEY and EXTERNAL_USER_ID are correctly set at the top of the script."
        )
        print("These values should be populated by the generation process.")
        print(f"Current API_KEY (from template): '{API_KEY}'")
        print(f"Current EXTERNAL_USER_ID (from template): '{EXTERNAL_USER_ID}'")
    else:
        print(
            f"Using API Key: {API_KEY[:4]}...{API_KEY[-4:] if len(API_KEY) > 8 else ''}"
        )
        print(f"Using External User ID: {EXTERNAL_USER_ID}")

        session_id = create_chat_session(API_KEY, EXTERNAL_USER_ID)

        if session_id:

            print("\n--- Testing Sync Mode ---")
            sync_query_text = "What is the capital of France? (sync)"
            sync_response_data = submit_query(
                API_KEY, session_id, sync_query_text, response_mode="sync"
            )
            if sync_response_data:
                print("Sync Response Data:")
                print(json.dumps(sync_response_data, indent=2))
            else:
                print("Failed to get sync response.")

            print("\n--- Testing Stream Mode ---")
            stream_query_text = (
                "Tell me a very short story, one sentence at a time. (stream)"
            )

            stream_result_status = submit_query(
                API_KEY, session_id, stream_query_text, response_mode="stream"
            )
            if stream_result_status:
                print(f"\nStream processing status: {stream_result_status}")
            else:
                print("Failed to get stream response.")
        else:
            print(
                "Failed to create chat session. Cannot proceed with submitting queries."
            )
