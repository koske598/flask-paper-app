from flask_wtf.form import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Regexp

class SerchWordForm(FlaskForm):
    keyword = StringField(
        "検索ワード",
        validators=[
            DataRequired(message="無効な文字が含まれています。英語での入力をお願いします。"), 
            Regexp("^[A-Za-z0-9!@#$%^&*()_+{}:\"<>?,./;'\[\]\\\-]*$")
            ],
        )
    
    year1 = IntegerField(
        "検索開始年",
        validators=[
            DataRequired(message="検索開始年が空です。")
        ]
    )

    year2 = IntegerField(
        "検索終了年",
        validators=[
            DataRequired(message="検索終了年が空です。")
        ]
    )
        
    submit = SubmitField('検索')
    
class ScrapyForm(FlaskForm):
    submit = SubmitField('再検索')
    
class DeleteForm(FlaskForm):
    submit = SubmitField('削除')