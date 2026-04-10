import secrets


def generate_uuid_hex():
    '''
    Generates a unique value (e.g., for filenames, IDs)
    '''

    return secrets.token_hex(32)


def user_profile_path(instance, filename):
    '''
    Generate the file path for uploading profile image.

    The uploaded file will be stored in the following format:
        MEDIA_ROOT/Users/<user-id>/profile/<unique_filename>.<extension>
    '''

    extension = filename.split('.')[-1]
    new_file_name = f'{generate_uuid_hex()}.{extension}'

    return f'media/Users/{instance.id}/profile/{new_file_name}'
