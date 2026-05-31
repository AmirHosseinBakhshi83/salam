from django import forms

class ExamAnswerForm(forms.Form):

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not questions:
            return

        for question in questions:
            if question.question_type == "multi_choice":
                self.fields[f"q{question.id}"] = forms.ChoiceField(
                    choices=[("A","A"),("B","B"),("C","C"),("D","D"),("E","E")],
                    required=False,
                    initial="-",
                    
                )

            elif question.question_type == "numeric":
                self.fields[f"q{question.id}"] = forms.DecimalField(
                    required=False,
                    initial="-1",
                )

            elif question.question_type == "true_false_set":
                for col in range(1, 6):
                    self.fields[f"q{question.id}_col{col}"] = forms.ChoiceField(
                        choices=[("-","---"),("T","ص"), ("F","غ")],
                        required=False,
                        initial="-",
                    )