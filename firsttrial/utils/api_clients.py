"""API client wrappers with error handling and retry logic."""

import os
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
import dashscope


class QwenClient:
    """Wrapper for DashScope Qwen API with error handling."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not found in environment")

        # Set base URL for international service
        dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

    def analyze_video(
        self,
        video_url: str,
        prompt: str,
        model: str = "qwen3-vl-32b-thinking",
        max_retries: int = 3
    ) -> str:
        """
        Analyze video with Qwen VL model.

        Args:
            video_url: URL or local path to video
            prompt: Analysis prompt
            model: Qwen model to use
            max_retries: Number of retry attempts on failure

        Returns:
            Response text from model
        """
        messages = [{
            "role": "user",
            "content": [
                {"video": video_url},
                {"text": prompt}
            ]
        }]

        for attempt in range(max_retries):
            try:
                response = dashscope.MultiModalConversation.call(
                    api_key=self.api_key,
                    model=model,
                    messages=messages
                )

                # Extract text from response
                try:
                    result_text = response.output.choices[0].message.content[0]["text"]
                except (IndexError, KeyError, TypeError):
                    # Try alternative formats
                    if hasattr(response.output, 'text'):
                        result_text = response.output.text
                    elif isinstance(response.output.choices[0].message.content, str):
                        result_text = response.output.choices[0].message.content
                    else:
                        raise Exception(f"Could not extract text from response: {response}")

                return result_text

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {e}")

    def analyze_video_streaming(
        self,
        video_url: str,
        prompt: str,
        model: str = "qwen3-omni-flash",
        modalities: List[str] = ["text"]
    ) -> str:
        """
        Analyze video with streaming Qwen model (supports audio).

        Args:
            video_url: URL to video
            prompt: Analysis prompt
            model: Qwen model (default: qwen3-omni-flash for audio support)
            modalities: Output modalities

        Returns:
            Complete response text
        """
        # Use OpenAI-compatible API for streaming models
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )

        completion = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "video_url", "video_url": {"url": video_url}},
                    {"type": "text", "text": prompt},
                ],
            }],
            modalities=modalities,
            stream=True,
            stream_options={"include_usage": True},
        )

        result_text = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                result_text += content
            elif not chunk.choices and hasattr(chunk, 'usage'):
                print(f"📊 Token usage: {chunk.usage}")

        return result_text


class OpenAIClient:
    """Wrapper for OpenAI API (including GPT-5)."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)

    def generate_with_reasoning(
        self,
        prompt: str,
        model: str = "gpt-5",
        reasoning_effort: str = "medium",
        text_verbosity: str = "low",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate response with GPT-5 reasoning model.

        Args:
            prompt: Input prompt
            model: Model to use (default: gpt-5)
            reasoning_effort: Reasoning depth (low/medium/high)
            text_verbosity: Output verbosity (low/medium/high)
            max_retries: Number of retry attempts

        Returns:
            Dict with 'output_text' and full response
        """
        for attempt in range(max_retries):
            try:
                result = self.client.responses.create(
                    model=model,
                    input=prompt,
                    reasoning={"effort": reasoning_effort},
                    text={"verbosity": text_verbosity},
                )

                return {
                    "output_text": result.output_text,
                    "full_response": result
                }

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"GPT-5 failed after {max_retries} attempts: {e}")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        max_retries: int = 3
    ) -> str:
        """
        Standard chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            max_retries: Number of retry attempts

        Returns:
            Response text
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                return response.choices[0].message.content

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"OpenAI API failed after {max_retries} attempts: {e}")
