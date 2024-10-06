# from tuition.student.schemas import StudentSignUp

# sign_up_data =  {
#             "full_name": "string",
#             "email": "bona6u0x@exweme.com",
#             "phone_number": "stringstri",
#             "password": "String#1",
#             "confirm_password": "String#1",
#             "field_of_interest": "string"
#             }
# def test_student_signup(fake_db_dependency, fake_student_utils, fake_institution_utils, test_client):
    
#     response = test_client.post(
#         "/student/signup",
#             json= sign_up_data
#         )
#     student_data = StudentSignUp(**sign_up_data)
#     assert fake_institution_utils.check_existing_email_called_once()
#     assert fake_student_utils.check_existing_email_called_once()
#     assert fake_student_utils.check_existing_email_called_once_with(sign_up_data.get('email'), fake_db_dependency)
#     assert fake_student_utils.create_student_called_once_with(student_data, fake_db_dependency)

