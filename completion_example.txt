ChatCompletion(
    id='gen-1789669300-sn4s4apqbCyOfVJMqW5Y', 
    choices=
        [
            Choice(
                finish_reason='stop', 
                index=0, 
                logprobs=None, 
                message=ChatCompletionMessage(
                    content='Hello! How can I help you today?', 
                    refusal=None, 
                    role='assistant', 
                    annotations=None, 
                    audio=None,
                    function_call=None, 
                    tool_calls=None, 
                    reasoning='\n\n', 
                    reasoning_details=[
                        {
                            'type': 'reasoning.text', 
                            'text': '\n\n', 
                            'format': 'unknown', 
                            'index': 0
                        }
                    ]
                ), 
                native_finish_reason='stop'
            )
        ], 
        created=1789669300, 
        model='nex-agi/nex-n2.5-mini:free', 
        object='chat.completion', 
        metadata=None, 
        moderation=None, 
        service_tier=None, 
        system_fingerprint=None, 
        usage=CompletionUsage(
            completion_tokens=13, 
            prompt_tokens=22, 
            total_tokens=35, 
            completion_tokens_details=CompletionTokensDetails(
                accepted_prediction_tokens=None, 
                audio_tokens=0, 
                reasoning_tokens=1, 
                rejected_prediction_tokens=None, 
                text_tokens=None, 
                image_tokens=0
            ), 
            prompt_tokens_details=PromptTokensDetails(
                audio_tokens=0, 
                cache_write_tokens=0, 
                cached_tokens=0, 
                image_tokens=None, 
                text_tokens=None, 
                video_tokens=0
            ), 
            cost=0, 
            is_byok=False,
            cost_details=
            {
                'upstream_inference_cost': 0,
                'upstream_inference_prompt_cost': 0,
                'upstream_inference_completions_cost': 0
            }), 
            provider='Nex AGI'
        )