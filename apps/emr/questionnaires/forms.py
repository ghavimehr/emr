from django import forms
from django.apps import apps
from django.utils import translation
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404

from apps.emr.lab.models import TestMeta
from .models import Meta


def get_questionnaire_form(request, lab_testmeta_id_value):
    """
    Returns a tuple (DynamicQuestionnaireForm, instructions) for the questionnaire.
    It determines the active language from the request and then:
      - Looks for instructions in Meta using the field "instruction_<lang>".
      - Uses level choices from fields "level_1_<lang>" ... "level_10_<lang>".
      - For each question field (q_n) in the answer model, looks up the corresponding
        row in the sheet and sets its label based on the field "<lang>_question",
        falling back to English if needed.
    """
    # 1. Fetch the Meta record for the given lab_testmeta_id.
    meta_record = get_object_or_404(Meta, lab_testmeta__pk=lab_testmeta_id_value)

    # 2. Get the questionnaire name from the linked TestMeta instance.
    testmeta_instance = meta_record.lab_testmeta
    questionnaire_name = testmeta_instance.name  # e.g., "YEMSQ"

    # Retrieve the all_required flag from TestMeta.
    all_required = testmeta_instance.all_required

    # 3. Dynamically load the sheet (questions) and answer models.
    try:
        sheet_model = apps.get_model("questionnaires", f"{questionnaire_name}Sheet")
        record_model = apps.get_model("questionnaires", questionnaire_name)
    except LookupError:
        return None

    # 4. Determine the active language; if none, default to "en"
    lang_code = translation.get_language()
    current_lang = lang_code.split("-")[0] if lang_code else "en"

    # 5. Get instructions from the Meta record for the current language.
    #    It looks for a field named "instruction_<current_lang>" (e.g., instruction_fa)
    #    and falls back to "instruction_en" if not present.
    instructions_field = f"instruction_{current_lang}"
    if hasattr(meta_record, instructions_field) and getattr(
        meta_record, instructions_field
    ):
        instructions = getattr(meta_record, instructions_field)
    else:
        instructions = meta_record.instruction_en

    # 6. Build the answer choices from the Meta record's level fields.
    #    It looks for "level_<i>_<current_lang>" and falls back to "level_<i>_en".
    choices = []
    for i in range(1, 11):
        level_field = f"level_{i}_{current_lang}"
        level_text = getattr(meta_record, level_field, None)
        if not level_text:
            level_text = getattr(meta_record, f"level_{i}_en", None)
        if level_text:
            choices.append((i, level_text))
    empty_choice = [("", _("options"))]
    final_choices = empty_choice + choices

    # 7. Create a dynamic ModelForm for the answer model.
    class DynamicQuestionnaireForm(forms.ModelForm):
        class Meta:
            model = record_model
            fields = [
                f.name for f in record_model._meta.fields if f.name.startswith("q_")
            ]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # For each answer field (e.g., q_1, q_2, ...), determine the label based on the sheet.
            for field_name in self.fields:
                if field_name.startswith("q_"):
                    try:
                        q_num = int(field_name.split("_")[1])
                    except (IndexError, ValueError):
                        q_num = None

                    sheet_row = (
                        sheet_model.objects.filter(pk=q_num).first() if q_num else None
                    )

                    # Default label is the field name if no matching row is found.
                    question_label = field_name
                    if sheet_row:
                        # Look for the question text in the current language (e.g., "fa_question")
                        question_field = f"{current_lang}_question"
                        if hasattr(sheet_row, question_field) and getattr(
                            sheet_row, question_field
                        ):
                            question_label = getattr(sheet_row, question_field)
                        else:
                            question_label = sheet_row.en_question

                    # Replace the field with a ChoiceField using our shared choices.
                    self.fields[field_name] = forms.ChoiceField(
                        choices=final_choices,
                        label=question_label,
                        required=(
                            True if all_required else self.fields[field_name].required
                        ),
                    )
                    # If all_required is True, override any default required setting.
                    if all_required:
                        self.fields[field_name].required = True

    return DynamicQuestionnaireForm, instructions
