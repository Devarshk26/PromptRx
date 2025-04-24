def format_prompt(original_text, category="instruction_simplification"):
    prompts = {
        "instruction_simplification": (
            "Simplify the following medical emergency room discharge instruction.\n"
            "Use clear, patient-friendly language that avoids all medical jargon.\n"
            "Do not invent or assume anything. Just simplify what is provided.\n"
            "Return only the simplified instruction, nothing more:\n\n"
        ),
        "medication_clarity": (
            "Rewrite the medication instruction below in simple, simplified language.\n"
            "Mention dose, timing, and any warnings.\n"
            "Do not add anything new.\n\n"
        ),
        "task_extraction": (
            "Extract and simplify only the core tasks from the instruction below.\n"
            "Return them as short, clear bullet points.\n"
            "Don't invent or explain anything.\n\n"
        ),
        "warning_highlight": (
            "Clearly restate any warning or danger signs in the instruction below.\n"
            "Use direct, serious, and simple language for the patient.\n"
            "Do not guess or add information.\n\n"
        ),
        "tone_support": (
            "Rephrase this instruction to be gentle and supportive.\n"
            "Keep it clear and easy to follow. Do not add information.\n\n"
        )
    }
    prompt_prefix = prompts.get(category, prompts["instruction_simplification"])
    return f"{prompt_prefix}{original_text.strip()}"
