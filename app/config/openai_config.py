OPENAI_CONFIG = {
    "default_settings": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 4000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    "model_specific_settings": {
        "o1": {
            "supported_params": ["max_completion_tokens"],
            "default_values": {
                "temperature": 1  # o1 models only support temperature=1
            },
            "param_mapping": {
                "max_tokens": "max_completion_tokens"
            }
        },
        "gpt": {
            "supported_params": [
                "temperature", 
                "top_p", 
                "max_tokens", 
                "frequency_penalty", 
                "presence_penalty"
            ]
        }
    },
    "model_descriptions": {
        "gpt-4": "Most capable GPT-4 model, better at complex tasks",
        "gpt-4-turbo-preview": "Latest GPT-4 model with improved performance",
        "gpt-3.5-turbo": "Fast and efficient for simpler tasks",
        "gpt-3.5-turbo-16k": "Same capabilities as standard GPT-3.5 but with 4x the context length",
        "o1-preview": "Advanced model with specialized capabilities (Tier 5)",
        "o1-mini": "Lightweight version of o1 model (Tier 5)"
    }
}
