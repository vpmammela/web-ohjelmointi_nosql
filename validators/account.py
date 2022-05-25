from errors.validation_error import ValidationError
from flask import request 


def validate_update_profile_picture(validate_update_profile_picture_func):
    def validate_update_profile_wrapper(*args, **kwargs):
        request_body = request.get_json()
        if request.method == 'GET':
            return validate_update_profile_picture_func(*args, **kwargs)
        elif request.method == 'PATCH':
            # mennään tänne, jos request_body lähetetään insomniasta
            if request_body:
                # jos profile picture-kenttä löytyy requst_bodysta,
                # kaikki on kunnossa ja voidaan mennä eteenpäin account_route_handleriin
                if 'profile_picture' in request_body:
                    return validate_update_profile_picture_func(*args, **kwargs)
                else:
                    # jos profile picture ei ole request_bodyssa, siitä nostetaan virhe
                    raise ValidationError('Profile picture is required')
            else:
                # tänne mennään, jos request bodya ei ole edes lähetetty (vasen sarake insomniassa)
                raise ValidationError('Body is required')
        
    return validate_update_profile_wrapper # huomaa, että funktio palautetaan ilman sulkjua () perässä




def check_profile_picture_max_size(max_size_in_kt=100):
    def wrapper(*args, **kwargs):
        request_body = request.get_json()
        base64_string = request_body['profile_picture']
        file_size = len(base64_string) * 3 / 4 - base64_string.count('=')
        file_size = file_size / 1000
        if file_size > 100:
            raise ValidationError('Image size must be under 100kB')
       
        return max_size_in_kt(*args,**kwargs)

    return wrapper

