from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms import IntegerField, FloatField, FileField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileAllowed


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    zip_code = StringField('ZIP/Postal Code', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Register')


class PetRegistrationForm(FlaskForm):
    name = StringField('Pet Name', validators=[DataRequired(), Length(max=100)])
    species = SelectField('Species', validators=[DataRequired()], 
                         choices=[('dog', 'Dog'), ('cat', 'Cat'), ('bird', 'Bird'), 
                                  ('rabbit', 'Rabbit'), ('hamster', 'Hamster'), 
                                  ('fish', 'Fish'), ('other', 'Other')])
    breed = StringField('Breed', validators=[Optional(), Length(max=100)])
    age = IntegerField('Age (in months)', validators=[Optional(), NumberRange(min=0)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    health_info = TextAreaField('Health Information', validators=[Optional(), Length(max=500)])
    behavior_info = TextAreaField('Behavior Information', validators=[Optional(), Length(max=500)])
    image = FileField('Pet Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Register Pet')


class DonationForm(FlaskForm):
    amount = FloatField('Donation Amount ($)', validators=[DataRequired(), NumberRange(min=1)])
    message = TextAreaField('Leave a Message (Optional)', validators=[Optional(), Length(max=500)])
    is_anonymous = BooleanField('Make Donation Anonymous')
    submit = SubmitField('Donate')


class ProfileUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    zip_code = StringField('ZIP/Postal Code', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Update Profile')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    species = SelectField('Filter by Species', validators=[Optional()],
                        choices=[('', 'All Species'), ('dog', 'Dogs'), ('cat', 'Cats'), 
                                ('bird', 'Birds'), ('rabbit', 'Rabbits'), 
                                ('hamster', 'Hamsters'), ('other', 'Other')])
    submit = SubmitField('Search')


class PetMatchForm(FlaskForm):
    species = SelectField('What type of pet are you looking for?', validators=[DataRequired()],
                         choices=[('dog', 'Dog'), ('cat', 'Cat'), ('bird', 'Bird'), 
                                 ('rabbit', 'Rabbit'), ('hamster', 'Hamster'), 
                                 ('fish', 'Fish'), ('other', 'Other')])
    
    age_preference = SelectField('Preferred age range', validators=[DataRequired()],
                               choices=[('baby', 'Baby/Young'), ('adult', 'Adult'), ('senior', 'Senior'), ('any', 'Any')])
    
    gender_preference = SelectField('Preferred gender', validators=[DataRequired()],
                                  choices=[('male', 'Male'), ('female', 'Female'), ('any', 'No preference')])
    
    size_preference = SelectField('Preferred size', validators=[Optional()],
                                choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('any', 'Any')])
    
    energy_level = SelectField('Preferred energy level', validators=[Optional()],
                             choices=[('low', 'Low/Calm'), ('medium', 'Medium'), ('high', 'High/Active'), ('any', 'Any')])
    
    good_with_children = SelectField('Must be good with children?', validators=[Optional()],
                                   choices=[('yes', 'Yes'), ('no', 'Not necessary')])
    
    good_with_other_pets = SelectField('Must be good with other pets?', validators=[Optional()],
                                     choices=[('yes', 'Yes'), ('no', 'Not necessary')])
    
    special_needs = SelectField('Willing to care for a pet with special needs?', validators=[Optional()],
                              choices=[('yes', 'Yes'), ('no', 'No')])
    
    living_environment = SelectField('Your living environment', validators=[Optional()],
                                   choices=[('apartment', 'Apartment'), ('house_small', 'Small House'), 
                                           ('house_large', 'Large House with Yard'), ('rural', 'Rural/Farm')])
    
    time_availability = SelectField('How much time can you spend with your pet daily?', validators=[Optional()],
                                  choices=[('minimal', 'Minimal (1-2 hours)'), ('moderate', 'Moderate (3-5 hours)'), 
                                          ('extensive', 'Extensive (6+ hours)')])
    
    training_preference = SelectField('Training preference?', validators=[Optional()],
                                    choices=[('already_trained', 'Already trained'), ('willing_to_train', 'Willing to train'), 
                                            ('professional_help', 'Will seek professional help')])
    
    submit = SubmitField('Find My Perfect Match')
