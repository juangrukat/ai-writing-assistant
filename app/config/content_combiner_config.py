"""Configuration for the Content Combiner Service."""

CONTENT_COMBINER_CONFIG = {
    'sections': {
        'prompt': {
            'prefix': "===Writing Prompt===\n",
            'suffix': "\n=====\n",
            'required': False,  # Prompt is optional
        },
        'submission': {
            'prefix': "===User Submission===\n",
            'suffix': "\n=====\n",
            'required': True,
        },
        'criteria': {
            'prefix': "===Evaluation Criteria===\n",
            'suffix': "\n=====\n",
            'required': True,
        },
    },
    'separator': "\n",
}
