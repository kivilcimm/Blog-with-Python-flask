from wtforms import Form,StringField,TextAreaField,PasswordField,validators

class RegisterForm(Form):
    name=StringField("Name",validators=[validators.Length(min=3, max=30)])
    surname=StringField("Surname",validators=[validators.Length(min=3, max=30)])
    username = StringField("User Name",validators=[validators.Length(min=3, max=30)])
    email = StringField("Email",validators=[validators.Email(message="Geçerli bir email adresi giriniz"),validators.DataRequired("Enter validate email")])
    password = PasswordField("Password",validators=[
        validators.DataRequired("Create password"),
        validators.length(min=8),
        validators.EqualTo(fieldname="confirm",message="Passwords do not match.Try again!!")])
    confirm=PasswordField("Confirm password")

class ArticleForm(Form):
    title=StringField("Title",validators=[validators.DataRequired("Create title"),validators.Length(min=6, max=50)])
    author=StringField("Author",validators=[validators.Length(min=6, max=50)])
    category=TextAreaField("Category",validators=[validators.DataRequired("Enter category"),validators.Length(min=1)])
    about=TextAreaField("About",validators=[validators.DataRequired("Enter a sentence about article"),validators.Length(min=1)])
    content=TextAreaField("Content",validators=[validators.DataRequired("Enter content of article"), validators.Length(min=100)])